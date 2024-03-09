import tkinter as tk
from tkinter import *
from tkinter.ttk import Combobox
from user import *
from database import *
from tkinter.scrolledtext import ScrolledText


#authenticationg the user
def login_check(username , password):
    if (get_user(username,password) != None):
        global User #global variable of the username
        User = username
        dashboard()
    else:
        Label(text="Invalid Username or password", fg="red").place(relx= .30, y = 120)
        
#removing all widget in the window
def clear_frame():
    for widget in window.winfo_children():
        widget.destroy()

#register frame
def register():
    def check_password_match(): #checking if password and confirm password matched other wise show an error
        if password_entry.get() == Cpassword_entry.get():
            registered(username_entry.get(),Cpassword_entry.get())
        else:
            pass_missmatch.config(text="Miss match password")

    clear_frame()
    username = ""
    password = ""
    Label(window,text="Please enter details below",width=300, height=2, bg="blue", font=("Calibri", 13),fg="white").pack()

    username_label = Label(text="Username :" )
    username_label.place(relx = .25 , y = 70)
    username_entry = Entry(textvariable=username)
    username_entry.place(relx = .40 , y = 70)


    password_label = Label(text="Password :")
    password_label.place(relx = .255 , y = 100)


    password_entry = Entry(window,show="*", textvariable=password)
    password_entry.place(relx = .40 , y = 100)

    pass_missmatch = Label(text="",fg = "red")
    pass_missmatch.place(relx=.40, y = 140 )

    Cpassword_label = Label(text="Confirm Password :")
    Cpassword_label.place(relx = .162 , y = 120)

    Cpassword_entry = Entry(window,show="*", textvariable=password)
    Cpassword_entry.place(relx = .40 , y = 120)

    Register = Button(window, text="Register",height=2, width=30, bd =5, command=lambda: check_password_match())
    Register.place(relx=.212, y = 200)

#frame for confirming that the account has been registered
def registered(user,password): 
    clear_frame()
    header = Label(window,text="Registered",width=300, height=2, bg="blue", font=("Calibri", 13), fg="white")
    header.pack()
    add_user(user,password)
    Label(text="Account has been registered!").pack(pady=10)
    dashboard_btn = Button(window, text="Dashboard",height=2, width=30, command=lambda: login_gui())
    dashboard_btn.pack(pady=10)

#main login frame
def login_gui():
    clear_frame()
    username = ""
    password = ""
    header = Label(window,text="Please enter username and password",width=300, height=2, bg="blue", font=("Calibri", 13), fg="white")

    username_label = Label(text="Username : " ,anchor="w")

    username_entry = Entry(textvariable=username)

    password_label = Label(text="Password :")

    password_entry = Entry(window,show="*", textvariable=password)


    Login_btn = Button(window, text="Log in",height=2, width=30, bd =5, command=lambda: 
                       login_check(username_entry.get(),password_entry.get()))
    header.pack()
    username_label.place(relx= 0.25 , y = 70)
    username_entry.place(relx = 0.40 , y = 70)
    password_label.place(relx= 0.25 , y = 100)
    password_entry.place(relx = 0.40 , y = 100)
    Login_btn.place(relx = 0.212 , y = 140)

#hover over effects on available parking list
def hoverOverEnter(event):
    event.widget['foreground'] = 'blue'
def hoverOverLeave(event):
    event.widget['foreground'] = 'black'

#click events on each available parking list to redirect for reservaton on the clicked slot
def clicked(val):
    y = 135
    InnerList = get_available_locations("inner")
    OuterList = get_available_locations("outer")
    Atext = Label(text=f"Available slots for Parking lot {val}")
    Atext.place(relx=.10,y=110)
    slots = []
    parking_label_list = []
    x = 0
    park_slot = 0

    if val == "Inner":
        slots = InnerList
    else:
        slots = OuterList

    posx = .10

    for item in slots: #creating a list of available slots to be clickale and hover over events
        parking_label_list.append(Label(text="",font=("Calibri",20,"bold","underline")))
        parking_label_list[x].config(text=item[0])
        parking_label_list[x].bind("<Enter>", hoverOverEnter)
        parking_label_list[x].bind("<Leave>", hoverOverLeave)
        parking_label_list[x].bind("<Button-1>", lambda e: reserve(e.widget.cget("text"),val))
        parking_label_list[x].place(relx = posx, y = y)
        y+= 40
        x+=1
        park_slot+=1
        if x%5 == 0:
            posx+= .1
            y = 135


#close connection to the database and return to the main login screen
def logout(): 
    close_database_connection()
    main_screen()
            
#main dashboard frame that can direct to the view parking list, reservation, feedback and logout
def dashboard():
    clear_frame()
    Label(text="Dashboard", bg="blue", width=300, height=2, font=("Calibri", 13), fg="white").pack()
    Label(text=f"Welcome {User}",width=300, height=2, font=("Calibri", 13)).pack()
    parking_btn = Button(window, text="Parking",height=2, width=30, command=lambda: parking())
    parking_btn.pack(pady=10)
    reserve_btn = Button(window, text="Reserve",height=2, width=30, command=lambda: reservation())
    reserve_btn.pack(pady=10)
    history_btn = Button(window, text="Feedback",height=2, width=30, command=lambda: feedback())
    history_btn.pack(pady=10)
    log_out_btn = Button(window, text="Logout",height=2, width=30, command=lambda: logout())
    log_out_btn.pack(pady=10)

#frame for viewing all of the available slots
def parking():
    clear_frame()
    Label(text="Parking", bg="blue", width=300, height=2, font=("Calibri", 13), fg="white").pack()
    Label(text="Select Parking lot : ").place(relx=.1,y = 55)
    data=("Inner", "Outer")
    cb=Combobox(window, values=data)
    cb.bind("<<ComboboxSelected>>", lambda _ : clicked(cb.get()))
    cb.place(relx=.10, y=80)

    dashboard_btn = Button(window, text="Dashboard",height=2, width=30, command=lambda: dashboard())
    dashboard_btn.place(relx=.10, rely = .85)



#frame for viewing current reservation and show its details. 
def reservation():
    user_reserve = get_reservations(User)
    def remove_res():
        remove_reservation(user_reserve[0][3])
        remove_btn.config(state="disabled")
        reservation_label.config(text = "Reservation has been removed!")

    clear_frame()
    location = ""

    Label(text="Parking", bg="blue", width=300, height=2, font=("Calibri", 13), fg="white").pack()
    if not user_reserve:
        reservation_label = Label(text="No Reservation")
    else:
        if user_reserve[0][3] > 20:
            location = "Outer"
        else:
            location = "Inner"
        dateTime = user_reserve[0][2].strftime(f"%m/%d/%Y, %H:%M:%S")
        strRes = f"Slot : {user_reserve[0][3]} \n Price: {user_reserve[0][1]} \n Expire at: {dateTime} \n Location: {location}"
        reservation_label = Label(text=strRes)
    
    reservation_label.pack()
    remove_btn = Button(window, text="Remove",height=2, width=30, command=lambda: remove_res())
    if not user_reserve:
        remove_btn.config(state="disabled")
    else:
        remove_btn.config(state="active")
    remove_btn.pack(pady=10)
    dashboard_btn = Button(window, text="Dashboard",height=2, width=30, command=lambda: dashboard())
    dashboard_btn.pack()

#logic for adding a reservation
def add_res(slot,hours):
    add_reservation(User,int(slot),int(hours))
    dashboard()

#frame for creating a reservation and selecting how many hours
def reserve(parking_slot, location):
    price = 2.35
    if location == "Outer":
        price = 4.32
    def calc_price():
        new_price = round(price * int(hours_entry.get()),2)
        price_label.config(text = f"${new_price}")

   
    clear_frame()
    Label(text=f"Reserve Parking for {parking_slot}", bg="blue", width=300, height=2, font=("Calibri", 13), fg="white").pack()
    Label(text="Hours: ").place(x=10,y = 70)
    hours_entry = Entry(textvariable="")
    Label(text="Price: ").place(x=10,y = 90)
    price_label = Label(text = f"${price}")
    Label(text=f"Loaction: {location}").place(x=10,y = 110)

    hours_entry.bind('<Return>', lambda _: calc_price())
    hours_entry.place(x = 60, y = 70)
    price_label.place(x=60,y = 90)
    reserve_btn = Button(window, text="Reserve",height=2, width=30, command=lambda: add_res(int(parking_slot),hours_entry.get()))
    reserve_btn.place(relx = .3, y = 150)
    reserve_btn = Button(window, text="Return",height=2, width=30, command=lambda: parking())
    reserve_btn.place(relx = .3, y = 190)

#frame for confirming that the feed back has been submmited
def feedback_submit_confirm():
    clear_frame()
    Label(text="FeedBack", bg="blue", width=300, height=2, font=("Calibri", 13), fg="white").pack()
    Label(text="Feedback has been submited").pack()
    dashboard_btn = Button(window, text="Return to Dashboard",height=2, width=30, command=lambda: dashboard())
    dashboard_btn.pack()

#frame for submiting a feedback
def feedback():
    def submit(): #logic for adding a feedback submited but the user
        add_comment(feedback_entry.get("1.0", tk.END),10)
        feedback_submit_confirm()
    clear_frame()
    Label(text="Feedback", bg="blue", width=300, height=2, font=("Calibri", 13), fg="white").pack()
    feedback_entry = ScrolledText(wrap = tk.WORD,width = 40,  height = 10)
    feedback_entry.place(relx = .1 , y = 70)
    feedback_submit_btn = Button(window, text="Submit Feed Back",height=2, width=30, command=lambda: submit())
    feedback_submit_btn.place(relx = .1, y = 240)
    dashboard_btn = Button(window, text="Return to Dashboard",height=2, width=30, command=lambda: dashboard())
    dashboard_btn.place(relx=.1, y = 300)

#main login frame of the app
def main_screen():
    clear_frame()
    Label(text="Choose Login Or Register", bg="blue", width=300, height=2, font=("Calibri", 13), fg="white").pack()
    Label(text="").pack()
    Login = Button(text="Login", height=2, width=30 , command=lambda: login_gui())
    Login.pack()
    Label(text="").pack()
    Register_Btn = Button(window, text="Register",height=2, width=30, command=lambda: register())
    Register_Btn.pack(pady=10)


window = tk.Tk()
window.title("Parking App")
window.geometry('500x500')

main_screen()
window.mainloop()