from customtkinter import CTk, CTkButton, CTkLabel, CTkScrollableFrame, CTkFrame, CTkFont, CTkEntry
from icecream import ic
import datetime
import os
import re

button_present=None

def create_gui():
    root = CTk()
    root.title("DRS Logs Analyser")
    root.geometry("800x600")

    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure((1), weight=2)
    root.grid_rowconfigure((0, 1, 2, 3, 4 ,5 ,6 ,7 ,8 ,9, 10), weight=1)


    # Scrollable frame for output label
    button_scrollable_frame = CTkScrollableFrame(root,label_text="Runs",)
    button_scrollable_frame.grid(row=0, column=0, rowspan=8, sticky="nsew")


       
    

  
    # Frame for output label (center)
    title_frame = CTkFrame(root, width=400, height=50)
    title_frame.grid(row=0, column=1)

    output_title_label=CTkLabel(title_frame,text="Run Information", font=CTkFont(size=20, weight="bold"))
    output_title_label.grid(row=0,column=1)

    output_frame = CTkFrame(root)
    output_frame.grid(row=1, column=1)

    output_label = CTkLabel(output_frame,font=CTkFont(size=18), text="ErrorText")
    output_label.grid(row=1, column=1)

    date_input_entry= CTkEntry(root,width=100)
    date_input_entry.grid(row=10,column=0)
   
    #Point to log folder path and generate list of files in log folder
    logs_folder_path="C:\\Users\\Basha\\OneDrive\\Desktop\\Logs"


    def check_log_path():
        try:
            if os.path.exists(logs_folder_path):
                global subdirectories
                subdirectories=[d for d in os.listdir(logs_folder_path) if os.path.isdir(os.path.join(logs_folder_path, d))]
                global run_folders
                run_folders=[folder for folder in subdirectories if folder.startswith("Run_")]

                # Get user-entered date
                user_date = get_date_input()

                # Filter run_folders based on date
                run_folders = [folder for folder in run_folders if check_folder_date(folder, user_date)]
                ic(run_folders)
    
        except Exception as e:
            print(f"Error accessing log folder: {e} ")


    def check_folder_date(folder, user_date):
       folder_path = os.path.join(logs_folder_path, folder)
       folder_creation_time = os.path.getctime(folder_path)
       folder_creation_date = datetime.datetime.fromtimestamp(folder_creation_time).date()
       ic(folder_creation_date)
       ic(user_date)
       return folder_creation_date <= user_date


    def get_date_input():
        date_input = date_input_entry.get()
        global date_input_check
        date_input_check=None
        try:
            # Convert user input to a date object (adjust date format as needed)
            date_object = datetime.datetime.strptime(date_input, "%d/%m/%Y").date()
            date_input_check=True
            return date_object
        except ValueError:
            print("Invalid date format. Please enter date in DD/MM/YYYY format.")
            return None


    #Remove "Run_" string from each run folder
    def clean_runs():
        try:
            global clean_run_folders
            clean_run_folders=[runs[4:] for runs in run_folders]
        except Exception as e:
            print(f"Error cleaning run folder names: {e}")

    def get_orderID(run_folder_path):
        if os.path.exists(run_folder_path):
            files = [f for f in os.listdir(run_folder_path) if os.path.isfile(os.path.join(run_folder_path, f))]

            rundef_file = next((file for file in files if file.endswith(".rundef")), None)

            if rundef_file:
                with open(os.path.join(run_folder_path, rundef_file), 'r') as f:
                    for line in f:
                        match = re.search(r"<OrderID>(\d+)\s", line)  # Use a regular expression to extract OrderID
                        if match:
                            global OrderID
                            OrderID = match.group(1)
                            ic(OrderID)
                            return OrderID

        return None  # Return None if OrderID not found
            
                   
   
    def search_run_folder(run_folder):
       
       global output_text
       output_text = ""
       empty_lines = "\n" * 2  # Adjust the number for desired spacing
       global run_folder_path
    
       run_folder_path = os.path.join(logs_folder_path, "Run_" + run_folder)

       if os.path.exists(run_folder_path):
                
            
                # Get files within the Run folder
            files = [f for f in os.listdir(run_folder_path) if os.path.isfile(os.path.join(run_folder_path, f))]
              

                # Check for error files
            error_file = next((file for file in files if file.endswith("Errors.csv")), None)
            ic(error_file)

            if error_file:
                error_file_path = os.path.join(run_folder_path, error_file)
                control_dispense_failure = check_error_file(error_file_path)
                error_message = "Error file found" 
                output_text += f"Run_{run_folder}:\n{error_message}{empty_lines}"
                ic(output_text)
                if control_dispense_failure:
                    output_text += f"Control Dispense Failure\n{empty_lines}"  
            else:
                output_text+= f"Run_{run_folder}:\nNo error file found\n{empty_lines}"



    def check_error_file(error_file_path):
        """Checks an error file for the string "Transfer from Control Plate".

        Args:
            error_file_path (str): Path to the error file.

        Returns:
            bool: True if the string is found, False otherwise.
        """
        with open(error_file_path, 'r') as error_file:
            for line in error_file:
                if "Transfer from Control Plate" in line:
                    return True
        return False

    def handle_button_click(run_folder):
            search_run_folder(run_folder)
            output_label.configure(text=output_text)  # Update output label with generated text
    


    def clear_grid():
        
        
        if button_present:
            button_frame.destroy()
        
        
    def create_buttons():
        
        check_log_path()
        clean_runs()
        global button_present
        global button_frame
        button_frame = CTkFrame(master=button_scrollable_frame, width=200)
        button_frame.pack(side="left", fill="y")  # Pack button_frame before creating buttons
        for run_folder in clean_run_folders:
            global button
            button = CTkButton(master=button_frame, text=run_folder, command=lambda folder=run_folder: handle_button_click(folder))
            button.grid(column=0, pady=5)
        
        button_present= True

    
    def search():
        get_date_input()
        if date_input_check:
            clear_grid()
            create_buttons()

    search_button=CTkButton(root,text="Search for Runs", command=search)
    search_button.grid(row=9, column=0)  
    


    

    root.mainloop()

create_gui()
