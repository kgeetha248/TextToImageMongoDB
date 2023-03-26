from pymongo import MongoClient
import streamlit as st
import easyocr as ocr # Optical Character Reader
from PIL import Image, ImageEnhance , ImageFilter , ImageOps # Image Processing - Pillow
import pandas as pd
import numpy as np

def readImage(image_read):
    reader=ocr.Reader(['en'])
    result=reader.readtext(image_read)    
    
    result_text = []  #Initializing a list to store the read texts

    for text in result: 
        result_text.append(text[1])
    
    df = pd.DataFrame.from_dict(result_text)

    return result_text
    
# To convert image to Binary File 
def convertToBinary(filename):
    with open(filename,'rb') as file:
        binarydata = file.read()
    return binarydata

# To convert Binary File to Image
def convertToFile(binarydata, filename):
    with open(filename,'wb') as file:
        file.write(binarydata)
        file.close()

#Creating an UI using Streamlit
def main():
    st.title("Text Extraction from Image")
    #reader=ocr.Reader(['en'])
    with st.container():

        image = st.empty()

        #st.subheader("Upload the image here")
        image = st.file_uploader(label= 'Upload your image here', type=['jpg','png','jpeg'], key = 'image')
        
        submit = st.button(label = 'Submit')

        if image:
        
            if "submit_state" not in st.session_state:
                st.session_state.submit_state = False
            
            if submit or st.session_state.submit_state:
                st.session_state.submit_state = True
            
            #if submit:
                input_image=Image.open(image)  # Read the image
                input_image.save(r"C:\Users\kgeet\OneDrive\Desktop\StreamlitImage.jpg") # Save the image locally
                #st.image(input_image)   #Display the image

                st.subheader("Choose any of the edited image below to display")

                # Cropping the image:
                # cropped_image = input_image.crop(box = (100,10,650,302))
                # if st.checkbox("Cropped Image"):
                #     st.image(cropped_image)

                # Re-sizing the image:
                resiz_img=input_image.resize((700,600))
                if st.checkbox("Resized Image"):
                    st.image(resiz_img)

                # gray scaling:
                gray_image = ImageOps.grayscale(resiz_img)
                
                # Improving the constrast:
                enhanced_image=ImageEnhance.Contrast(gray_image)
                Contrast_image = enhanced_image.enhance(12)
                if st.checkbox("Enhanced Image"):
                    st.image(Contrast_image)

                # Thresholding - image is catogorized into two classes - above and below threshold:
                threshold = 125
                threshold_image = Contrast_image.point(lambda p : p > threshold and 255 )
                if st.checkbox("Thresholded Image"):
                    st.image(threshold_image)   

                # Sharpening the image:
                sharp_image = ImageEnhance.Sharpness(Contrast_image)
                sharpened_image = sharp_image.enhance(12)
                if st.checkbox("Sharpened Image"):
                    st.image(sharpened_image)
                        
                st.subheader("To display the text from image, Click below")
                #if st.checkbox("Display Details"):


                display = st.button("Display Details",key = 1)
                # upload = st.button("Upload to DB", key = 2)  

                #Initialize Session_state:
                if "display_state" not in st.session_state:
                    st.session_state.display_state = False
                
                if display or st.session_state.display_state:
                    st.session_state.display_state = True

                    with st.spinner("Reading...!"):

                        readtext_list = readImage(np.array(Contrast_image))
                        
                        readtext_dict = {str(key):[data] for key, data in enumerate(readtext_list)}
                        #readtext_dict=df_edited.to_dict("records")
                        
                        df = pd.DataFrame.from_dict(readtext_dict)

                        df_edited = df.melt(ignore_index=True)

                        st.dataframe(df_edited)
                        print(readtext_dict)
                        
                        #st.balloons()
                                            
                        #Mongodb Connection

                        #To display the extracted details:
                                                                    
                        upload = st.button("Upload to DB")

                        #Initialize Session_state:
                        if "upload_state" not in st.session_state:
                            st.session_state.upload_state = False
                        
                        if upload or st.session_state.upload_state:
                            st.session_state.upload_state = True

                            if upload:

                                pyConnect = MongoClient("mongodb://kgeetha248:guvidw34@ac-3kffpy5-shard-00-00.utmmzha.mongodb.net:27017,ac-3kffpy5-shard-00-01.utmmzha.mongodb.net:27017,ac-3kffpy5-shard-00-02.utmmzha.mongodb.net:27017/?ssl=true&replicaSet=atlas-oz6uib-shard-0&authSource=admin&retryWrites=true&w=majority")
                                pyDB=pyConnect["geetha"]    # database 
                                pyCollection=pyDB["Bizcard"]   # Collection

                                #readtext_dict=df_edited.to_dict("records")

                                insert = pyCollection.insert_many([readtext_dict])

                                st.success("Successfully Uploaded")

    tab_titles = ["Retrieve Details" , "Update Details" , "Delete Record"]

    tabs = st.tabs(tab_titles)

        # column_2 , column_3 , column_4 = st.columns(3)

        #Retriving from DB:
    with tabs[0]:

        with st.form(key = "form_2", clear_on_submit = True):

            id_input = st.text_input("Enter the name", key = 'id')
        
            retrieve = st.form_submit_button("Retrieve Details") 

            if "retrieve_state" not in st.session_state:
                    st.session_state.retrieve_state = False
                
            if retrieve or st.session_state.retrieve_state:
                    st.session_state.retrieve_state = True
                
                    with st.spinner("Retrieving..!"):

                        if retrieve:

                            pyConnect = MongoClient("mongodb://kgeetha248:guvidw34@ac-3kffpy5-shard-00-00.utmmzha.mongodb.net:27017,ac-3kffpy5-shard-00-01.utmmzha.mongodb.net:27017,ac-3kffpy5-shard-00-02.utmmzha.mongodb.net:27017/?ssl=true&replicaSet=atlas-oz6uib-shard-0&authSource=admin&retryWrites=true&w=majority")
                            pyDB=pyConnect["geetha"]    # database 
                            pyCollection=pyDB["Bizcard"]   # Collection

                            data_dict = []
                            for x in pyCollection.find({'0': str(st.session_state["id"])}):
                                print(x)
                                data_dict.append(x)
                            if data_dict:
                                data_dataframe = pd.DataFrame(data_dict)
                                st.dataframe(data_dict)
                            else:
                                st.error("Details not found")
                            
                      
                
    # Update Database
    with tabs[1]:
                                        
        update_name = st.text_input("Enter name to update", key = "update_name") 

        update_col = st.text_input("Enter the column to update ",key = "update_col")
        
        update_value = st.text_input("Enter the details to update", key = 'update_value')

        update = st.button("Update")

        if "update_state" not in st.session_state:
            st.session_state.update_state = False
            
        if update or st.session_state.update_state:
            st.session_state.update_state = True

        if update:  

            # Update Query
            pyConnect = MongoClient("mongodb://kgeetha248:guvidw34@ac-3kffpy5-shard-00-00.utmmzha.mongodb.net:27017,ac-3kffpy5-shard-00-01.utmmzha.mongodb.net:27017,ac-3kffpy5-shard-00-02.utmmzha.mongodb.net:27017/?ssl=true&replicaSet=atlas-oz6uib-shard-0&authSource=admin&retryWrites=true&w=majority")
            pyDB=pyConnect["geetha"]    # database 
            pyCollection=pyDB["Bizcard"]   # Collection

            query1 = {"0" : str(st.session_state['update_name'])}
            value1 = { "$set" : {str(st.session_state["update_col"]) : str(st.session_state["update_value"])}}
            pyCollection.update_one(query1,value1)

            data_dict = []
            for x in pyCollection.find({'0': str(st.session_state["update_name"])}):
                print(x)
                data_dict.append(x)
            if data_dict:
                data_dataframe = pd.DataFrame(data_dict)
                st.dataframe(data_dict)
            else:
                st.error("Details not found")
           
            
    # Delete Record:
    with tabs[2]:

        delete_id = st.text_input("Enter the name to delete", key = "delete_id")
                                            
        delete = st.button("Delete details")
        
        if delete:

            pyConnect = MongoClient("mongodb://kgeetha248:guvidw34@ac-3kffpy5-shard-00-00.utmmzha.mongodb.net:27017,ac-3kffpy5-shard-00-01.utmmzha.mongodb.net:27017,ac-3kffpy5-shard-00-02.utmmzha.mongodb.net:27017/?ssl=true&replicaSet=atlas-oz6uib-shard-0&authSource=admin&retryWrites=true&w=majority")
            pyDB=pyConnect["geetha"]    # database 
            pyCollection=pyDB["Bizcard"]   # Collection
            
            #Delete Query
            query4 = {"0" : str(st.session_state['delete_id'])}
            pyCollection.delete_one(query4)
            st.success("Details Deleted")             

main()                    
