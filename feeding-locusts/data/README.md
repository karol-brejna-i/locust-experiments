This experiment loads a csv file and distributes its content among locust workers.

The file that the actual scripts are using is placed in [locust-scripts](../locust-scripts) directory.

The following section describes the content of the file and how the data can be obtained.

## Test dataset

Source: [chess-db.com](https://chess-db.com/public/execute.jsp?age=99&sex=a&countries=all).

The dataset is a list of top-ranked chess players with the following attributes:
* No
* chess-db ID
* name
* title
* federation country
* ELO rating
* national ELO rating
* year of birth
* additional info (i = inactive, w = woman)
* number of games played
* club/city
* ???
  
[obtain.py script](./obtain.py) can be used to obtain the fresh version of the data.

The following column names are used for respective attributes. 

| Number | Id        | name                    | title | Fed           | Elo   | NElo | Born  | flag | Games | Club/City       | #Trns |
| -----: | --------: | ----------------------- | ----- | ------------- | ----- | ---- | ----- | ---- | ----- | --------------- | ----- |
| 1      | 1503014   | "Carlsen Magnus"        | GM    | Norway        | 2839  |      | 1990  |      |       | OSG Baden-Baden | 230   |
| 2      | 2020009   | "Caruana Fabiano"       | GM    | USA           | 2827  |      | 1992  |      |       |                 | 987   |
| 3      | 13401319  | "Mamedyarov Shakhriyar" | GM    | Azerbaijan    | 2820  |      | 1985  |      |       |                 | 190   |
| 4      | 4100018   | "Kasparov Garry"        | GM    | Russia        | 2812  |      | 1963  | i    |       |                 | 10    |

The script writes comma delimited `data.csv` file in the current directory.

## Alternative datasets
The code of the experiment "doesn't care" about the data it uses. 
If you want to play with your own data, make sure it is a comma separated CSV file.