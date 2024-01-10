import cv2
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

def match_template_in_thread(template_path, large_image, gray_large_image, template_size, threshold, matched_filenames):
    template_file = os.path.basename(template_path)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    
    if template is None:
        print(f"Error loading template: {template_path}")
        return
    
    template = cv2.resize(template, template_size)
    
    # Perform template matching
    result = cv2.matchTemplate(gray_large_image, template, cv2.TM_CCOEFF_NORMED)
    
    # Get the location of matched regions
    locations = np.where(result >= threshold)
    
    # Check if any matches were found
    if locations[0].size > 0:
        # Remove the .png ending from the filename
        filename_without_extension = os.path.splitext(template_file)[0]
        matched_filenames.append(filename_without_extension)
        
        # Draw rectangles around matched regions
        for pt in zip(*locations[::-1]):
            w, h = template.shape[::-1]
            cv2.rectangle(large_image, pt, (pt[0] + w, pt[1] + h), (0, 255, 0), 2)

def match_images_to_board(board, max_threads=24):
    start_time = time.time()

    # Path to the larger image
    large_image_path = board

    # Path to the folder containing template images
    template_folder = "images2"

    # Desired size for template images
    template_size = (206, 180)

    # Load the larger image and convert to grayscale
    large_image = cv2.imread(large_image_path)
    gray_large_image = cv2.cvtColor(large_image, cv2.COLOR_BGR2GRAY)

    # List to store matched template filenames
    matched_filenames = []

    # Create a thread pool with a limited number of threads
    with ThreadPoolExecutor(max_threads) as executor:
        # Iterate over each template image in the folder using threads from the pool
        for template_file in os.listdir(template_folder):
            template_path = os.path.join(template_folder, template_file)
            executor.submit(match_template_in_thread, template_path, large_image, gray_large_image, template_size, 0.80, matched_filenames)

    # Display or save the result
    #cv2.imshow("Result", large_image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    # Print the matched filenames
    print("Matched filenames:", matched_filenames)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time} seconds")
    return matched_filenames, large_image

# Call the function to match images to the board with a maximum of 4 threads
