# ArrayMagic
KLayout Array template, inspired by fourms post :
https://www.klayout.de/forum/discussion/2572/

# Installation and setup
* This package works as a KLayout PCell plugin, installation can be done byy placing the main scrip file `Lib_ArrayMagic.lym` under folder path `~\KLayout\pymacros\`
* After installation, an `FunctionArray` PCell can be accessed from application toolbar `Instance` --> Library `ArrayMagic` --> cell `FunctionArray`

# Use case and example
An example gds can be found under forder `Example`
![image](https://github.com/user-attachments/assets/267cf6b6-cec5-4265-b6b3-8b985fdc3345)

# Function and parameters

### Fields:
![image](https://github.com/user-attachments/assets/ada7d5d5-258d-429f-8dbf-b2c861087d36)

* Function fields utilize python `evals` to process the value, single line of python script can be accepted.
* The returned value will be taked as the assigned value to field.
* Only generic type of function and data type is supported, oythin library `math` is also supported.
* Looping using list comprehension and ternary operation is allowed.
* Looping through element in row-column order, and the function field is evaluated and assigned in top to bottom order
* Default value will be applyed it script failed to ececute.


1. X position function [`Float`, default = 0    ] :
   - Assign current element X location by function return value, in a unit of `um`.

2. Y position function [`Float`, default = 0    ] :
   - Assign current element Y location by function return value, in a unit of `um`.

3. Rotation   function [`Float`, default = 0    ] : 
   - Assign current element rotation by function return value, in a unit of `degreed`.

4. Mirror     function [`Bool`,  default = False] : 
   - Assign current element mirror by function return value, takes a boolean value.

5. VIsibility function [`Bool`,  default = False] : 
   - Assign whether insert current element to layout, takes a boolean value.



### parameters:
* `WIDTH` : Array element width value applied from pcell panel
* `HEIGHT`: Array element height value applied from pcell panel
* `ROWS`  : Array Row counts applied from pcell panel
* `COLS`  : Array Column counts applied from pcell panel
* `COL`   : Current element column number (iterated from 0 ~ (`COLS`-1))
* `ROW`   : Current element row number (iterated from 0 ~ (`ROWS`-1))
* `Xpos`  : Current element calculated X position, avaliable for field Y, Rotation, Mirror and Visibility
* `Ypos`  : Current element calculated Y position, avaliable for field Rotation, Mirror and Visibility
* `ROT`   : Current element calculated Rotation, avaliable for field Mirror and Visibility
* `MIR`   : Current element calculated Mirror, avaliable for field  Visibility, (Mirrior to Y-axis)



