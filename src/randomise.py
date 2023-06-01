import os
import random
import shutil

# Set the root directory
root_dir = 'models/gan/27-05-2023/run_1/results/images'

# Set the number of questions and images per question
num_questions = 10
num_gt = 3
num_col = 1

# Set the total number of images needed
total_gt = num_questions * num_gt
total_col = num_questions * num_col
output_dir = 'selected_images/gan_survey'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get the list of image directories
image_dirs = sorted(os.listdir(root_dir))

# Shuffle the image directories
random.shuffle(image_dirs)

# Iterate through the image directories
for i in range(num_questions):
    # Create a directory for each question
    question_dir = os.path.join(output_dir, f'question{i+1}')
    os.makedirs(question_dir, exist_ok=True)
    
    # Select random image directories for ground truth and colorized images
    selected_dirs = random.sample(image_dirs, num_gt + num_col)
    
    # Copy ground truth images to the question directory
    for j in range(num_gt):
        src_path = os.path.join(root_dir, selected_dirs[j], 'ground_truth.png')
        dst_path = os.path.join(question_dir, f'{j+1}.png')
        shutil.copy(src_path, dst_path)
    
    # Copy colorized image to the question directory
    src_path = os.path.join(root_dir, selected_dirs[num_gt], 'colourised.png')
    dst_path = os.path.join(question_dir, 'col.png')
    shutil.copy(src_path, dst_path)

    # Remove the selected directories from the list
    image_dirs = [dir_name for dir_name in image_dirs if dir_name not in selected_dirs]

print('Images selected and saved successfully.')