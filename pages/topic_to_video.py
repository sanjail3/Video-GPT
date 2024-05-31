import streamlit as st
import tempfile
import os
from VideoGPT.core.video_generator import VideoGenerator
st.set_page_config(page_title="Topic to Video", page_icon="📷", layout="centered")
import time




def init():

    session_variables = [
        "video_script",
        "audio_path",
        "voice_option",
        "image_prompts",
        "script_parts",
        "image_paths",
        "video_path",
    ]
    for variable in session_variables:
        if variable not in st.session_state:
            st.session_state[variable] = None


def generate_video():

    try:
        video_generator = VideoGenerator()
        with st.form(key="generate_video_form"):
            col1, col2 = st.columns(2)
            with col1:
                topic = st.text_input(
                    "Enter Topic 📝",
                    placeholder="3 scary places in the world",
                )
                duration = st.number_input(
                    "Enter Duration (seconds) ⏳", min_value=1, max_value=120, value=30
                )
                duration = str(duration) + "s"
                tone = st.text_input("Enter Tone 🎵", placeholder="scary")

                voice_uuid=st.text_input("Enter your Resemble voice uuid ")
                voice_uuid=str(voice_uuid)

            with col2:
                instructions = st.text_input(
                    "Enter Instructions ✍️", placeholder="Add my name in the script"
                )
                language = st.selectbox(
                    "Select Language 🌐", video_generator.get_languages()
                )
                num_of_images = st.number_input(
                    value=5, min_value=1, max_value=20, label="Number of Images 🖼️"
                )
                project_uuid = st.text_input("Enter your Resemble project uuid ", placeholder='Optional')
                project_uuid = str(project_uuid)
            _, center, _ = st.columns([2, 3, 1])
            temp_dir = tempfile.TemporaryDirectory()
            with center:
                submit_button = st.form_submit_button(label="Generate Script 🚀")

            if submit_button:
                with st.spinner("Generating Script"):
                    generated_script = video_generator.generate_script(
                        topic,
                        duration=duration,
                        tone=tone,
                        instructions=instructions,
                        language=language,
                        num_of_images=num_of_images,
                    )
                if generated_script is None:
                    st.error("Error generating video")

                else:
                    st.success("Script generated successfully")
                    st.session_state.video_script = generated_script
        if st.session_state.video_script is not None:
            col1, col2 = st.columns(2)
            title = st.session_state.video_script["video_title"]
            description = st.session_state.video_script["video_description"]
            script_parts = st.session_state.video_script["script_parts"]
            image_prompts = st.session_state.video_script["image_prompts"]

            with col1:
                st.text_input("Title 📌", value=title)
                st.text_area("Description 📝", value=description)

            with col2:
                with st.expander("Script 📜 "):
                    for i, part in enumerate(script_parts):
                        st.text_input(f"Part {i+1} ✏️", value=part, key=f"part{i+1}")

                with st.expander("Image Prompts 🖼️"):
                    for i, prompt in enumerate(image_prompts):
                        st.text_input(
                            f"Prompt {i+1} ✏️", value=prompt, key=f"prompt{i+1}"
                        )

            with col2:
                with st.expander("Audio Options 🎵 "):
                    voice_option = st.selectbox(
                        options=['Male','Female'],
                        label="Voice 🔊",
                    )


                font_color = "#ffff00"
                font = None
                font_size = 70

            _, center, _ = st.columns([3, 2, 3])
            with center:
                submit_button = st.button("Generate Video 🎥")

            if submit_button:

                temp_dir = tempfile.TemporaryDirectory()




                with st.spinner("Generating voice for your video"):
                    st.info("Generating audio takes 30-60 seconds")
                    try:


                        audio_path = os.path.join(temp_dir.name , "voice.mp3")

                        print(os.path.exists(audio_path))

                        updated_script_parts = []
                        for i in range(len(script_parts)):
                            updated_script_parts.append(st.session_state[f"part{i+1}"])
                        updated_image_prompts = []
                        for i in range(len(image_prompts)):
                            updated_image_prompts.append(
                                st.session_state[f"prompt{i+1}"]
                            )

                        print(updated_script_parts, updated_image_prompts)
                        video_generator.generate_audio(
                            output_file=audio_path,
                            script_parts=updated_script_parts,
                            voice_uuid=voice_uuid,
                            project_uuid=project_uuid
                        )


                        st.session_state.audio_path = audio_path
                    except Exception as e:
                        print(e)
                        st.error("Error generating audio")

                if st.session_state.audio_path is not None:
                    st.audio(st.session_state.audio_path, format="audio/mp3")

                with st.spinner("Generating images for your video"):
                    st.info("Generating one image takes 20-30 seconds")
                    try:
                        image_path = os.path.join(temp_dir.name, "images")
                        # mk folder if not exists
                        os.makedirs(image_path, exist_ok=True)
                        image_paths = video_generator.generate_images(
                            image_prompts=updated_image_prompts,
                            image_path=image_path,
                        )
                        st.session_state.image_paths = image_paths
                    except Exception as e:
                        print(e)
                        st.error("Error generating images")

                if st.session_state.image_paths is not None:
                    num_of_images = len(st.session_state.image_paths)
                    cols = st.columns(num_of_images)
                    for i, col in enumerate(cols):
                        col.image(st.session_state.image_paths[i])

                    with st.spinner("Generating video"):
                        try:
                            st.info("Generating video takes 60 seconds")
                            output_file = "video.mp4"
                            video_path = video_generator.generate_video(
                                video_dir=temp_dir.name,
                                output_file=output_file,
                                subtitle_options={
                                    "font_color": font_color,
                                    "font_size": font_size,
                                    "font": font,
                                },
                            )
                            st.session_state.video_path = video_path
                        except Exception as e:
                            print(e)
                            st.error("Error generating video")

                    if st.session_state.video_path is not None:
                        _, center, _ = st.columns([1, 1, 1])
                        center.video(st.session_state.video_path)

    except Exception as e:
        st.error(f"Error: {e}")
        st.error(
            "Please try again later",
        )


def main():


    try:
        _, img_col, _ = st.columns([1, 3, 1])
        img_col.image("./static/images/VideoGPTlogo.png")
        st.header(
            " 📽️ Just Enter the Theme of the Video Let Me Generate Video For You !!! ",

        )
        generate_video()

    except Exception as e:
        st.error(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    init()
    main()


