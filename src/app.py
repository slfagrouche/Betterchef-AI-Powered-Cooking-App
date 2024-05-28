# gradio_interface
import gradio as gr
from utils import *
from dotenv import load_dotenv


def create_interface():
    with gr.Blocks() as app:
        gr.Markdown("<h1 style='text-align: center;'>👨‍🍳 Better Chef 👩‍🍳</h1>")
        gr.Markdown("### Whisk up your culinary skills! Explore recipes, watch cooking tutorials, and get tips from our cheeky AI—spicing up your cooking has never been more fun! 🎉🍳")

        with gr.Accordion("Image Upload and Dish Suggestions"):
            with gr.Row():
                with gr.Column():
                    image_input = gr.Image(label="Upload an Image", type="pil")
                    submit_image = gr.Button("Submit Image")
                with gr.Column():
                    suggestions_output = gr.Textbox(label="Suggested Dishes", interactive=False, placeholder="Dishes will be suggested here.")
            submit_image.click(get_dish_suggestions, inputs=image_input, outputs=suggestions_output)

        with gr.Accordion("Select Dish"):
            dish_choice = gr.Textbox(label="Type the dish you're interested in", placeholder="Enter a dish from the suggestions above.")

        with gr.Column(elem_id="center-column"):
            with gr.Accordion("Get Recipes"):
                submit_recipe = gr.Button("Get Recipe")
                recipe_output = gr.Textbox(label="Recipe", interactive=False, visible=False)
                submit_recipe.click(fn=get_recipe, inputs=dish_choice, outputs=recipe_output, show_progress=False)
                submit_recipe.click(lambda: gr.update(visible=True), None, recipe_output)

            with gr.Accordion("Search for Cooking Videos"):
                submit_video = gr.Button("Get Video")
                videos_output = gr.HTML()
                submit_video.click(fn=lambda dish_choice: generate_embed_html(search_youtube_videos(dish_choice)), inputs=dish_choice, outputs=videos_output)

            with gr.Accordion("AI Assistant for Cooking Queries"):
                with gr.Row():
                    with gr.Column():
                        question = gr.Textbox(label="Ask the AI Assistant", placeholder="Type your question here.")
                        submit_question = gr.Button("Ask AI")
                    with gr.Column():
                        ai_response = gr.Textbox(label="AI Assistant Response", interactive=True)
                chat_log = gr.State([])
                submit_question.click(fn=ai_assistant_interaction, inputs=[dish_choice, question, chat_log], outputs=[ai_response])

            # Clear button to reset all fields
            clear_button = gr.Button("Clear All")
            clear_button.click(
                fn=clear_all,
                outputs=[image_input, suggestions_output, dish_choice, videos_output, recipe_output, ai_response, chat_log]
            )
    return app


app = create_interface()
app.launch(share=True)



