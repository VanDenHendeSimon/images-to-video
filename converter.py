import os
import tkinter
import tkinter.filedialog
import re
import moviepy.editor


def convert(selected_image):
    """
    Renders a movie, given a single image,
    if that image is part of an image sequence, by:

    Going through the directory of the selected image

    Storing all images in the same sequence by comparing frame numbers,
    as well as a simplified basename

    Storing all movies that could cause a conflict when writing the new movie

    Checking these movies and creating a basename that is worry-free

    Writing the movie to disk

    :param selected_image: Any image in the image sequence selected by the user
    :return: movie of the images
    """

    """
    Prepare the input
    """
    # Extract info from selected image
    directory = os.path.dirname(selected_image)
    selected_image = os.path.basename(selected_image)
    selected_image_type = os.path.splitext(selected_image)[1]

    # Strip out frame numbers and extension from the sequence
    # to get more generic image name

    # 1. Remove extention
    generic_image_name = selected_image.rstrip(selected_image_type)
    # 2. Fetch frame digits
    frame_digits = re.findall("\\d+", generic_image_name)
    # 3. Strip out the frame digits
    generic_image_name = generic_image_name.rstrip(
        frame_digits[len(frame_digits)-1]
    )

    """
    Go through the files and store movies and images
    that are important for the job
    """
    images = []
    movies = []

    # Collect files in selected folder
    for current_file in sorted(os.listdir(directory)):
        # Check if the current file is a video previously saved by this script
        if current_file.endswith('.mp4') and '_v' in current_file:
            movies.append(current_file)

        # Check if the current file contains the generic image name
        # and has the same file type
        elif (
            generic_image_name in current_file and
            current_file.endswith(selected_image_type)
        ):
            if len(images) > 0:
                # Compare the frame numbers to make sure
                # the current file is next in line
                # Strip out the generic name from the current file name
                current_frame = int(
                    os.path.splitext(
                        current_file[len(generic_image_name):]
                    )[0]
                )
                # Get last image in the list,(= the previous frame)
                last_image_basename = os.path.basename(images[len(images)-1])
                # Get this image's frame number
                last_image_frame = int(
                    os.path.splitext(
                        last_image_basename[len(generic_image_name):]
                    )[0]
                )

                # If this is the case, add the current file to the list
                if current_frame == last_image_frame+1:
                    images.append((directory + '/' + current_file))
            else:
                # If there are no images to compare with, add the current one
                images.append((directory + '/' + current_file))

    """
    Determine the version of the video
    """
    if len(movies) == 0:
        # Set starting version if no previous movies have been rendered here
        version = '001'
    else:
        # Initialize highest version
        highest_version = 1

        for movie in movies:
            # Extract version of the currently looked at mp4 file,
            # which could cause overwriting issues
            current_version = int(re.search(r'v([0-9]+)', movie).group(1))
            # Update highest version
            if current_version >= highest_version:
                highest_version = current_version + 1

        # Increment highest version
        version = '{0:03d}'.format(highest_version)

    """
    Prepare and write the video
    """
    # Set frames per second
    fps = 24

    # Store images and prepare for writing
    clips = [moviepy.editor.ImageClip(m).set_duration(1.0/fps) for m in images]
    concat_clip = moviepy.editor.concatenate_videoclips(
        clips, method='compose'
    )

    # # Check clip properties video
    # if concat_clip.size[0] > 1920 and concat_clip.size[1] > 1080:
    #     concat_clip.resize(width=1920, height=1080)

    # Store resolution
    resolution = '%dx%d' % (concat_clip.size[0], concat_clip.size[1])

    # Set video location
    video_name = '%s/%s%dfps_v%s_%s.mp4' % (
        directory, generic_image_name, fps, version, resolution
    )

    # Write video
    concat_clip.write_videofile(video_name, fps=fps)

    """
    Some follow up for the user's experience
    """
    # Open file folder
    os.startfile(os.path.dirname(video_name))


def browse():
    """
    Opens up an explorer window that lets you select a file,
    I then made sure the file type is valid and passed it to the converting def
    """
    # Initialize file browser
    root = tkinter.Tk()
    root.withdraw()

    # Select root folder
    title = 'Please select any image in the sequence you want to convert'
    selected_file = tkinter.filedialog.askopenfilename(
        parent=root, initialdir="/", title=title
    )

    # Check if the selected file is an image
    possible_file_types = ['tiff', 'tga', 'exr', 'jpg', 'jpeg', 'png']
    if any(file_type in selected_file for file_type in possible_file_types):
        # Call for conversion
        convert(selected_file)


browse()
