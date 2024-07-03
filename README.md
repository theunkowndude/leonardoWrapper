# Image Generation with Leonardo Library

This document outlines the process of generating images using the `Leonardo` library in Python, as demonstrated in the provided code snippet.

## Overview

The code snippet demonstrates how to use the `Leonardo` class from the `leonardoWrapper` module to generate an image based on a textual prompt. The example generates an image of a fantastical scene inside an ancient, otherworldly library.

## Steps

1. **Initialization**: The `Leonardo` class is initialized with a username and password.

    ```python
    from leonardoWrapper import Leonardo

    leonardo = Leonardo(username="your_username", password="your_password")
    ```

    > **Note**: Replace `your_username` and `your_password` with your actual credentials.

2. **Creating an Image Generation Request**: An image generation request is created with specific parameters such as the prompt, number of images, model ID, model version, image dimensions, and guidance scale.

    ```python
    get_generation_id = leonardo.create_generate_image(
        prompt="Create a fantastical and visually stunning scene inside an ancient, otherworldly library...",
        amount_of_images=1,
        model_id="model_id",
        sd_version="model_version", # for some models you have to provide the sd_version
        width=1024,
        height=768,
        guidance_scale=7
    )
    ```

    > **Note**: Replace `model_identifier` and `model_version` with the specific model ID and version you wish to use. For a list of available models and their versions, see [models.md](https://github.com/theunkowndude/leonardoWrapper/edit/main/models.md). Please note that you can run `gen_models_md.py` to update the documentation with the latest model information.
    

3. **Waiting for Image Generation**: The script waits for the image generation process to complete.

    ```python
    leonardo.wait_for_image_generation(creation_id=get_generation_id)
    ```

4. **Retrieving the Generated Image**: The generated image is retrieved, and its details are printed.

    ```python
    generated_image = leonardo.get_image_generation(creation_id=get_generation_id)

    print(generated_image)
    print(generated_image["generated_images"][0]["url"])
    ```

## Conclusion

This guide introduces the fundamental steps for generating images with the Leonardo library. It encompasses the initialization of the Leonardo class, formulation of an image generation request, supervision of account management throughout the generation phase, and the final retrieval of the created image.
