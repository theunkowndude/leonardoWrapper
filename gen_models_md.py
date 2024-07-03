from leonardoWrapper import Leonardo

leonardo = Leonardo(username="", password="")

keys_to_remove = ["instancePrompt", "modelHeight", "modelWidth", "createdAt"]


def remove_keys_from_dict(dict_obj, keys):
    if isinstance(dict_obj, dict):
        return {k: remove_keys_from_dict(v, keys) for k, v in dict_obj.items() if k not in keys}
    elif isinstance(dict_obj, list):
        return [remove_keys_from_dict(item, keys) for item in dict_obj]
    else:
        return dict_obj


cleaned_data = remove_keys_from_dict(leonardo.user.get_global_models(), keys_to_remove)


markdown_output = "# Models\n\n"
for model in cleaned_data['data']['custom_models']:
    markdown_output += f"## {model['name']}\n"
    markdown_output += f"**ID:** {model['id']}\n\n"
    markdown_output += f"**Description:** {model['description']}\n\n"
    markdown_output += f"**Core Model:** {model['coreModel']}\n\n"
    markdown_output += f"**SD Version:** {model['sdVersion']}\n\n"
    markdown_output += f"**Type:** {model['type']}\n\n"
    markdown_output += f"**NSFW:** {model['nsfw']}\n\n"
    markdown_output += f"**Public:** {model['public']}\n\n"
    markdown_output += f"**Training Strength:** {model['trainingStrength']}\n\n"
    markdown_output += f"**User:** {model['user']['username']}\n\n"

    markdown_output += "<details>\n"
    markdown_output += "   <summary>Click to view a example</summary>\n\n"
    if model.get('generated_image'):
        markdown_output += f"![Generated Image]({model['generated_image']['url']})\n\n"
    if model.get('generations'):
        markdown_output += "### Generations\n\n"
        for generation in model['generations']:
            markdown_output += f"**Prompt:** {generation['prompt']}\n\n"
            for image in generation['generated_images']:
                markdown_output += f"![Generated Image]({image['url']})\n\n"
    markdown_output += "</details>\n\n"
    markdown_output += "---\n\n"


with open("models.md", "w") as file:
    file.write(markdown_output)
file.close()
