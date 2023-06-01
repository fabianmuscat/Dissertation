from enum import Enum
import os, re, cv2, csv
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm

from keras.utils import img_to_array
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.model_selection import train_test_split

# from skimage.metrics import structural_similarity as ssim
from skimage import io, metrics, color
from PIL import ImageOps, Image
import tensorflow as tf
from tensorflow.keras.applications import VGG16

# region =========================================== CONSTANTS ===========================================

API_KEY = "710903625f43af5a9bb567f640317ef9ae45b77ee231a59cd6a2665a7c9e768f"
DATASET = "/content/dataset"
CSV_HEADERS = ["Image", "MSE", "SSIM", "PSNR"] # "RMSE"
IGNORE = [".DS_Store", "Icon", "Icon?"]

BATCH_SIZE = 50
EPOCHS = 100
IMAGE_SIZE = 160
TRIALS = 5

# endregion

# region =========================================== ENUMS ===========================================

class Levels(Enum):
    INFO = 1
    SUCCESS = 2
    ERROR = 3
    WARNING = 4
    
class MODELS(Enum):
    AE = "./models/ae", "h5"
    GAN = "./models/gan", "h5"

# endregion

# region =========================================== HELPER FUNCTIONS ===========================================

def log(level: Levels, text: str):
    print(f"[{level.name}] {text}")

def log_ln(level: Levels, text: str):
    print(f"[{level.name}] {text}\n")

def sort_alnum(data):
    """Sorts data alpha-numerically

    Args:
        data (list): The data to be sorted
    """    
    def alphanum_key(key):
        return [int(c) if c.isdigit() else c.lower() for c in re.split("([0-9]+)", key)]
    
    return sorted(data, key=alphanum_key)

# region ======================= MODELS =======================

def preprocess(path, limit = None, resize = None): 
    """This function preprocesses image data by loading images from a specified 
    directory and converting them to float32 format. The images are resized if 
    required and then returned as a tuple of RGB or grayscale images depending on 
    the directory specified.The function takes the following parameters:
    
    path : str
        The path to the directory containing images.
    limit : int, optional
        The maximum number of images to preprocess. Default is None, meaning all images are preprocessed.
    resize : int, optional
        The height and width dimension to which the images are resized. Default is None, meaning no resizing is done.
        
    The function returns a tuple of two lists, where the first list contains resized or original RGB images, and the second list contains resized or original grayscale images.
    """
    colour, gray = [], []
    dirs = [os.path.join(path, directory) for directory in next(os.walk(path))[1]]

    for dir_path in dirs:
        dir_name = os.path.basename(dir_path)
        if dir_name not in ("COLOUR", "GRAY"):
            continue

        to_remove = os.path.join(dir_path, ".DS_Store")
        if os.path.exists(to_remove):
            os.remove(to_remove)

        files = os.listdir(dir_path)
        for ign in IGNORE:
            if ign in files:
                files.remove(ign)
            
        files = files[:limit] if limit != None else files
        files = sort_alnum(files)
        for img in tqdm(files, desc=dir_name):
            img = cv2.imread(os.path.join(dir_path, img), 1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            if resize != None:
                img = cv2.resize(img, (resize, resize))

            img = img.astype("float32") / 255.0
            labels = {"COLOUR": colour, "GRAY": gray}
            target_list = labels.get(dir_name)
            target_list.append(img_to_array(img))

        log_ln(Levels.SUCCESS, "Prepocessing done.")

    return np.array(colour), np.array(gray)

def get_dataset(dataset_name, train_size, num_images = None):
    dataset = os.path.join(DATASET, dataset_name)
    if not os.path.exists(dataset):
        raise FileNotFoundError(f"{dataset_name} not found in {DATASET}")

    colour_imgs, gray_imgs = preprocess(dataset, limit=num_images, resize=IMAGE_SIZE)
    gray_train, gray_test, colour_train, colour_test = train_test_split(gray_imgs, colour_imgs, train_size=train_size, random_state=1)

    gray_train = np.reshape(gray_train, (len(gray_train), IMAGE_SIZE, IMAGE_SIZE, 3))
    colour_train = np.reshape(colour_train, (len(colour_train), IMAGE_SIZE, IMAGE_SIZE, 3))

    gray_test = np.reshape(gray_test, (len(gray_test), IMAGE_SIZE, IMAGE_SIZE, 3))
    colour_test = np.reshape(colour_test, (len(colour_test), IMAGE_SIZE, IMAGE_SIZE, 3))

    return [gray_train, gray_test, colour_train, colour_test]

def concat_datasets(dataset_names, test_size, num_images = None):
    colour_train_list = []
    colour_test_list = []
    colour_val_list = []
    gray_train_list = []
    gray_test_list = []
    gray_val_list = []

    for dataset_name in dataset_names:
        colour_train, colour_test, colour_val, gray_train, gray_test, gray_val = get_dataset(dataset_name, test_size, num_images)
        colour_train_list.append(colour_train)
        colour_test_list.append(colour_test)
        colour_val_list.append(colour_val)
        gray_train_list.append(gray_train)
        gray_test_list.append(gray_test)
        gray_val_list.append(gray_val)

    colour_train = np.concatenate(colour_train_list)
    colour_test = np.concatenate(colour_test_list)
    gray_train = np.concatenate(gray_train_list)
    gray_test = np.concatenate(gray_test_list)

    return [colour_train, colour_test, colour_val, gray_train, gray_test, gray_val]


def plot_images(color, grayscale, predicted=None, save_path=None, show=False):
    num_cols = 3 if type(predicted).__name__ != 'NoneType'  else 2
    fig, axes = plt.subplots(ncols=num_cols, figsize=(15, 15))
    titles = ["Ground Truth", "Grayscale", "Colourised"] if predicted is not None else ["Ground Truth", "Grayscale"]

    for (ax, title, img) in zip(axes, titles, [color, grayscale, predicted]):
        ax.set_title(title, fontsize=15)
        ax.imshow(img)
        ax.set_axis_off()

        if save_path is not None:
            if not os.path.exists(f"{save_path}"): os.mkdir(f"{save_path}")
            if title == "Grayscale": continue
            plt.imsave(f"{save_path}/{title.lower().replace(' ', '_')}.png", img)

    if show:
        fig.show()

def get_metrics(ground_truth, colourised):
    gt_image = io.imread(ground_truth)
    colorized_image = io.imread(colourised)
    
    mse = metrics.mean_squared_error(gt_image, colorized_image)
    ssim = get_ssim(gt_image, colorized_image)
    psnr = metrics.peak_signal_noise_ratio(gt_image, colorized_image)
    
    return {
        'MSE': round(mse, 3), # Mean Squared Error (MSE)
        'SSIM': round(ssim.numpy(), 3), # Structural Similarity Index (SSIM)
        'PSNR': round(psnr, 3) # Peak Signal-to-Noise Ratio (PSNR)
    }

def write_to_csv(path_to_csv, data):
    with open(path_to_csv, 'w', encoding="UTF8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(data)

def generate_paths(model: MODELS) -> dict:
    path, ext = model.value
    now = datetime.now()
    day_dir = os.path.join(path, now.strftime("%d-%m-%Y"))
        
    if not os.path.exists(path): os.mkdir(path)
    if not os.path.exists(day_dir): os.mkdir(day_dir)
    
    runs = os.listdir(day_dir)
    if ".DS_Store" in runs:
        to_remove = os.path.join(day_dir, ".DS_Store")
        os.remove(to_remove)
    
    sorted_dirs = sorted([int(run.split("_")[1]) for run in runs if run != ".DS_Store"]) if len(runs) > 0 else [0]
    run_dir = os.path.join(day_dir, f"run_{sorted_dirs[-1] + 1}")
    
    results_dir = os.path.join(run_dir, "results")
    images_dir = os.path.join(results_dir, "images")
    
    os.mkdir(run_dir)
    os.mkdir(results_dir)
    os.mkdir(images_dir)

    return {
        'WEIGHTS': os.path.join(run_dir, f"weights.{ext}"),
        'RUN': run_dir, 
        'RESULTS': results_dir,
        'IMAGES': images_dir
    }

def compare(ground_truth, predicted):
    def mse(imageA, imageB):
        # the 'Mean Squared Error' between the two images is the sum of the squared difference between the two images
        mse_error = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
        mse_error /= float(imageA.shape[0] * imageA.shape[1])
            
        # return the MSE. The lower the error, the more "similar" the two images are.
        return mse_error
    
    # Import images
    image1 = cv2.imread(ground_truth)
    image2 = cv2.imread(predicted, 1)

    # Convert the images to grayscale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Check for same size and ratio and report accordingly
    ho, wo, _ = image1.shape
    hc, wc, _ = image2.shape
    ratio_orig = ho/wo
    ratio_comp = hc/wc
    dim = (wc, hc)

    if round(ratio_orig, 2) != round(ratio_comp, 2):
        print("\nImages not of the same dimension. Check input.")
        exit()

    # Resize first image if the second image is smaller
    elif ho > hc and wo > wc:
        print("\nResizing original image for analysis...")
        gray1 = cv2.resize(gray1, dim)

    elif ho < hc and wo < wc:
        print("\nCompressed image has a larger dimension than the original. Check input.")
        exit()

    if round(ratio_orig, 2) == round(ratio_comp, 2):
        mse_value = mse(gray1, gray2)
        ssim_value = ssim(gray1, gray2)
        return [mse_value, ssim_value]
    
    return []

def perform_cross_val(model, x, y, parameters: dict, cv_fold, checkpoint):
    scorers = {
        "ssim": make_scorer(metrics.structural_similarity),
        "psnr": make_scorer(metrics.peak_signal_noise_ratio)
    }
    
    grid_cv = GridSearchCV(model, parameters, cv=cv_fold, scoring=scorers, refit=False)
    grid_cv.fit(x, y, epochs=EPOCHS, batch_size=BATCH_SIZE, callbacks=[checkpoint])
    return grid_cv, pd.DataFrame(grid_cv.cv_results_)

def generator_loss(y_true, y_pred):
    return tf.reduce_mean(tf.square(y_pred - y_true))

def discriminator_loss(y_true, y_pred):
    return 0.5 * (tf.reduce_mean(tf.square(y_true - 1)) + tf.reduce_mean(tf.square(y_pred)))

def get_ssim(y_true, y_pred):
    return tf.reduce_mean(tf.image.ssim(y_true, y_pred, max_val=1.0)) 

# endregion

# endregion