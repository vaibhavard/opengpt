        icon="()"
        del helper.data["systemMessage"]   


        try:
            del helper.data["message"]  
            icon=icon+"(history)"
        except:
            pass
        try:
            helper.processed_text=""
            del data["context"]
            icon=icon+"(context)"
        except:
            pass
        try:
            helper.uploaded_image=""
            del data["imageBase64"]
            icon=icon+"(image)"

        except:
            pass
        try:
            del data["imageURL"]
            icon=icon+"(imageurl)"
        except:
            pass