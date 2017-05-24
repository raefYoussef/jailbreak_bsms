JAILBREAK BSMS
===

AUTHORS
---

Ahmed Refai

Raef Youssef

Tul Parajuli 

George Esakandar

EMAIL: jailbreakbsms@gmail.com  
Copyright (C) 2017 JailbreakBSMS Capstone Team

Dashboard  
---  
The dashboard includes information about the operation of the brewery during the previous week.

**Status Panels**  
The status panels show the number of shipped, filled, tapped, and returned kegs during the past week. Clicking on ‘view details’ displays information about which kegs were shipped/filled/tapped/returned.
 
**Inventory Status**  
A line graph that tracks how many kegs were, added/returned, cleaned, filled, placed on tap, and shipped. 

**Beer Brands**  
A donut chart that displays the beer brands for kegs that are full in the inventory and kegs which are placed on tap.

**Customers**  
A table that displays information about customers, keg count and last activity for the past week.

View Inventory  
---  
The View Inventory page displays all kegs currently entered in the inventory system.

**Sort**  
The table displayed on the inventory allows you to sort by column in both directions (ascending and descending). Simply click on the header for the column you would like to sort to initiate a sort.

**Advanced Search**  
Clicking the “Advanced Search” option will reveal the advanced search menu. This allows you to filter all results in the table. You can search kegs by ID, by date, by beer brand, or even by customer.  
To reset a search, click on the “Advanced Search” button again.

**Delete**  
Click the row/rows you would like to delete to select them. Once they are selected, they should be highlighted in blue, click the red delete button in the bottom left hand corner to delete the kegs from the inventory. This is the best option in the event where a keg is unavailable for scanning (lost, damaged, stolen, etc.)

Edit Inventory  
---  
The Edit Inventory page makes use of the RFID scanner and tags, Users can scan tags one by one or multiple at the same time. New kegs can be added, existing kegs can be edited, or finally, removed from the inventory.

**Scan Tag**  
Clicking the “Start Scan” button will wait and listen for the scanner to scan the desired kegs. The scan data is then printed to the textarea. After all the kegs are scanned, clicking “Stop Scan” will stop listening for any input and update kegs on either of the tables described below.


**Inventory**  
The Inventory table will display all the scanned kegs that are already in inventory. Users can delete any number of kegs after clicking “Delete”. This will delete the entry from the database.  
The user can select any row(s) to edit or update by clicking on “Edit & Update” button.  A single pop up menu will appear prompting the user to enter relevant information about the kegs in question.  
**ID:** The keg ID’s of the selected kegs appear in the ID box.  
**Keg Type:** Choose from HB or QB. More can be added from within MariaDB.  
**Status:** Choose from a drop down menu of possible statuses.  
**Beer Brand:** Choose from a drop down menu of possible beer brands. See Settings page to add a beer brand if your desired beer brand is not there. The beer brand field is automatically cleared when the keg is cleaned. This field should not be cleared manually by the user when setting keg status to dirty as this will interfere with the functionality of the logistics page.  
**Customer:** Enter the name of the customer if the keg is being shipped out. Similar to beer brand, this field will automatically clear when the keg is cleaned. The user should not clear the field manually.
Notes: Enter any notes you may wish to include to be visible in the inventory.

**NOTE:** When multiple kegs are selected, all the above selections (with the exception of ID) will be applied to all currently selected kegs.

Click the Submit button to confirm and edit the database.
To view your changes, rescan the desired kegs, or search for them in the View Inventory page.

**Unidentified Kegs**  
The Unidentified Kegs table will display all the scanned kegs that are new to the database. User can delete it from the page by clicking on “Delete” button. User can click on “Edit & Add” button to edit the new keg information one at a time or multiple IDs at once, then add it to the database.

Logistics  
---  
The logistics page displays information which can increase the productivity of the brewery.  

**Customers**  
Gives more details about customers, last activity, lifetime keg total, current keg total, least recent shipment, and the most preferred beer brands. 

**Note:** the keg count subtracts the number of times a keg was shipped minus the number of times it was returned. If the user tries to ship a shipped keg or return a returned keg, the keg count column will contain inaccurate information. For more accurate information about how many kegs a customer has not returned (keg count), refer to dashboard page. The dashboard page contains information from the current inventory whereas the logistics page contain information about the history of the inventory. 
  
**Beer Brand Demand (Shipped)**  
Gives information about which beer brands are most shipped. This graph tracks the frequency of shipped keg brands across the year. 

**Beer Brand Demand (Tapped)**  
Gives information about which beer brands are most served in the tap room. This graph tracks the frequency of tapped keg brands across the year. 

Settings
---
The settings page is designed for users to change password, Admin to add new users, add new beer brands to the database, and make any beer brand active or inactive.

**Change Password**  
Admin or any user can change their password by providing current login email and password.

**Add New User**  
Only Admin can add new user by providing new email, name, and password.

**Add Beer Brand**  
Anyone logged into the system can add a new Brand Brand to the database by entering Beer Brand Name and clicking the “Submit” button.

**Change Beer Brand Status**  
This section will list all the Beer Brand that are already on the system. Then, the user can make any item Active or Inactive by clicking on “Active” or “Inactive” button.
