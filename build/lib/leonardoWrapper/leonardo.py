import sys
import time
from typing import Literal

from leonardoWrapper.types.GeneratedImage import GeneratedImage
from leonardoWrapper.user.user import User
from leonardoWrapper.util.api import RequestsHandler

sys.dont_write_bytecode = True

class Leonardo:
    def __init__(self, username: str, password: str) -> None:
        self._requests_handler = RequestsHandler()
        self.user = User(username=username, password=password, requests_handler=self._requests_handler)


    def create_generate_image(self, prompt: str, model_id: str, negative_prompt: str = "", nswf: bool = False, image_size: int = 7, sd_version: str = None, amount_of_images: int = 4, width: int = 1368, height: int = 768, num_inference_steps: int = 10, guidance_scale: int = 7, scheduler: str = None, tiling: bool = False, public: bool = False, leonardo_magic: bool = False, enhance_prompt: bool = True, contrast: float = 3.5, preset_style: str = None, pose_to_image: bool = False, pose_to_image_type: str = "POSE", weighting: float = 0.75, high_contrast: bool = False, transparency: Literal["enabled", "disabled"] = "disabled", photo_real: bool = False) -> str:
        """
        Create a task to generate an image based on the provided prompt.
        Parameters:
            - prompt: The prompt based on which the image will be generated.
            - negative_prompt: A description of elements or themes to be excluded from the generated image.
            - model_id: The model to be used for generating the image.
            - nswf: Whether the generated image should be safe for work.
            - image_size: The size of the generated image.
            - sd_version: The version of the model to be used for generating the image.
            - amount_of_images: The number of images to be generated.
            - width: The width of the generated image.
            - height: The height of the generated image.
            - num_inference_steps: The number of inference steps to be taken.
            - guidance_scale: The stronger the guidance scale, the more the generated image will reflect the prompt, it must be between 1 and 20.
            - scheduler: The scheduler to be used for generating the image.
            - tiling: Whether to use tiling for generating the image.
            - public: Whether the generated image should be public.
            - leonardo_magic: Whether to use Leonardo Magic for generating the image.
            - enhance_prompt: Enhance the prompt.
            - pose_to_image: Whether to use pose to image for generating the image.
            - pose_to_image_type: The type of pose to image.
            - weighting: The weighting of the generated image.
            - high_contrast: Whether to use high contrast for generating the image.
            - transparency: Whether to use transparency for generating the image.
            - photo_real: Whether to use photo real for generating the image.
        """

        if guidance_scale < 1 or guidance_scale > 20:
            raise ValueError("guidance_scale must be between 1 and 20.")


        make_request = self._requests_handler.send_graphql_request(
            json_data={
                "operationName": "CreateSDGenerationJob",
                "variables": {
                    "arg1": {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "nsfw": nswf,
                        "num_images": amount_of_images,
                        "width": width,
                        "height": height,
                        "image_size": image_size,
                        "num_inference_steps": num_inference_steps,
                        "contrast": contrast,
                        "guidance_scale": guidance_scale,
                        "sd_version": sd_version,
                        "modelId": model_id,
                        "presetStyle": preset_style,
                        "scheduler": scheduler,
                        "public": public,
                        "tiling": tiling,
                        "leonardoMagic": leonardo_magic,
                        "poseToImage": pose_to_image,
                        "poseToImageType": pose_to_image_type,
                        "weighting": weighting,
                        "highContrast": high_contrast,
                        "elements": [],
                        "userElements": [],
                        "controlnets": [],
                        "photoReal": photo_real,
                        "transparency": transparency,
                        "styleUUID": "111dc692-d470-4eec-b791-3475abac4c46",
                        "enhancePrompt": enhance_prompt,
                        "collectionIds": []
                    }
                },
                "query": "mutation CreateSDGenerationJob($arg1: SDGenerationInput!) { sdGenerationJob(arg1: $arg1) { generationId __typename } }"
            }
        )

        if "errors" in make_request["json"]:
            raise Exception(make_request["json"]["errors"][0]["message"])

        try:
            return make_request["json"]["data"]["sdGenerationJob"]["generationId"]
        except:
            raise Exception("Failed to create the image generation task.")


    def wait_for_image_generation(self, creation_id: str, check_interval: int = 5) -> None:
        while True:
            try:
                get_status = self._requests_handler.send_graphql_request(
                    json_data={
                        "operationName": "GetAIGenerationFeedStatuses",
                        "variables": {
                            "where": {
                                "status": {
                                    "_in": [
                                        "COMPLETE",
                                        "FAILED"
                                    ]
                                },
                                "id": {
                                    "_in": [
                                        creation_id
                                    ]
                                }
                            }
                        },
                        "query": "query GetAIGenerationFeedStatuses($where: generations_bool_exp = {}) { generations(where: $where) { id status __typename } }"
                    }
                )

                if get_status["json"]["data"]["generations"] != []:
                    break
                else:
                    time.sleep(check_interval)

            except:
                raise Exception("Failed to get the status of the image generation.")



    def get_image_generation(self, creation_id: str):
        get_solution = self._requests_handler.send_graphql_request(
            json_data={
                "operationName": "GetAIGenerationFeed",
                    "variables": {
                        "where": {
                            "userId": {
                                "_eq": self.user.user_informations["user_id"]
                            },
                            "teamId": {
                                "_is_null": True
                            },
                            "canvasRequest": {
                                "_eq": False
                            },
                            "universalUpscaler": {
                                "_is_null": True
                            },
                            "isStoryboard": {
                                "_eq": False
                            },
                            "id": {
                                "_in": [
                                    creation_id
                                ]
                            }
                        },
                        "offset": 0,
                        "limit": 10
                    },
                "query": "query GetAIGenerationFeed($where: generations_bool_exp = {}, $userId: uuid, $limit: Int, $offset: Int = 0) { generations( limit: $limit offset: $offset order_by: [{createdAt: desc}] where: $where) { modelId scheduler coreModel sdVersion prompt negativePrompt id status quantity createdAt public nsfw custom_model { id userId name modelHeight modelWidth } generated_images(order_by: [{url: desc}]) { id url nsfw } } }"
            }
        )



        generated_image = GeneratedImage(
            {
                "nsfw": get_solution["json"]["data"]["generations"][0]["nsfw"],
                "model_id": get_solution["json"]["data"]["generations"][0]["modelId"],
                "scheduler": get_solution["json"]["data"]["generations"][0]["scheduler"],
                "coreModel": get_solution["json"]["data"]["generations"][0]["coreModel"],
                "sdVersion": get_solution["json"]["data"]["generations"][0]["sdVersion"],
                "prompt": get_solution["json"]["data"]["generations"][0]["prompt"],
                "negativePrompt": get_solution["json"]["data"]["generations"][0]["negativePrompt"],
                "status": get_solution["json"]["data"]["generations"][0]["status"],
                "quantity": get_solution["json"]["data"]["generations"][0]["quantity"],
                "createdAt": get_solution["json"]["data"]["generations"][0]["createdAt"],
                "public": get_solution["json"]["data"]["generations"][0]["public"],
                "nsfw": get_solution["json"]["data"]["generations"][0]["nsfw"],

                "generated_images": [
                    {
                        "id": image["id"],
                        "url": image["url"],
                        "nsfw": image["nsfw"]
                    } for image in get_solution["json"]["data"]["generations"][0]["generated_images"]
                ]
            }
        )

        try:
            generated_image.update(
                {
                    "custom_model": {
                        "id": get_solution["json"]["data"]["generations"][0]["custom_model"]["id"],
                        "userId": get_solution["json"]["data"]["generations"][0]["custom_model"]["userId"],
                        "name": get_solution["json"]["data"]["generations"][0]["custom_model"]["name"],
                        "modelHeight": get_solution["json"]["data"]["generations"][0]["custom_model"]["modelHeight"],
                        "modelWidth": get_solution["json"]["data"]["generations"][0]["custom_model"]["modelWidth"]
                    },
                }
            )
        except:
            pass


        return generated_image