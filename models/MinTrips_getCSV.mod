/*********************************************
 * OPL 12.8.0.0 Model
 * Author: Luigi Berducci
 * Creation Date: 27/nov/2018 at 17:16:52
 *********************************************/
 
 /***************************************************************************************/
 /*                   CONSTANTS, PARAMETERS AND ADDITIONAL VARIABLES				   	*/
 /***************************************************************************************/
 /* Declare parameters */
 int numStudents = ...;	/* Total number of students */
 int numDays	 = ...; /* Total number of days, even if there are not all the shifts*/
 int numShifts	 = ...; /* Number of shifts in a day */
 int MaxNumShiftsPerDay = ...;  /* Max number of assignment to a student in the same day */

 /* Define helping variable "big M" */
 int BigM        = 1000;

 /* Define ranges according to the parameters */
 range students = 1..numStudents;
 range days 	= 1..numDays;
 range shifts 	= 1..numShifts;
 
 /* Declare strings for student, day and shift names (e.g. "Luigi Berducci", "Mon 01 Dec", "09:30-10:30" ...) */
 string StudNames[students] = ...;
 string DayNames[days] 		= ...;
 string ShiftNames[days] 		= ...;
 
 /* Declare 3D array of availability */
 int Availability[students][days][shifts] = ...;
 
 /* Declare the 2D array of existance of shifts 
 	This is useful for missing shifts (e.g. the 3rd shift on Friday). */
 int Existance[days][shifts] = ...;
 
 /* Declare the array of minimum number of shifts for each student */
 int MinNumShifts[students]  = ...;
 int MaxNumShifts[students]  = ...;
 
 /* Take init time to compute statistics */
 float temp;
 execute{
	var before = new Date();
	temp = before.getTime();
 }
 
 /***************************************************************************************/
 /*                              MODELING MILP PROBLEM				   	                */
 /***************************************************************************************/
 /* DECISION VARIABLES */
 /* X[s][d][t] == 1, the shift t on day d is assigned to the student s */
 /* X[s][d][t] == 0, otherwise */
 dvar int X[students][days][shifts] in 0..1;
 /* AssignedShifts[s] is the number of shifts assigned to the student s (controlled redundancy) */
 dvar int AssignedShifts[students];
 /* Trips[s,d] is a flag which indicates that the student s must go to the library in the day d (controlled redundancy) */
 dvar int Trips[students, days] in 0..1;
 /* AvgShifts is the average number of shifts assigned (controlled redundancy) */
 dvar float AvgShifts;

 /* OBJECTIVE FUNCTION */
 /* Minimize the number of shifts to cover all the month. */
 minimize sum(s in students) sum(d in days) Trips[s][d];
 
 /* CONSTRAINTS */
 subject to {
      /* Consistency definition of Trips[students, days] (redundancy) */
      /* if X[s][d][t1] + ... + X[s][d][tN] > 0 -> Trips[s][d]=1 */
      forall(s in students)
          forall(d in days)
              (sum(t in shifts) X[s][d][t]) - BigM*Trips[s, d] <= 0;

      /* Consistency definition of AssignedShifts[students] (redundancy) */
      forall(s in students)
        AssignedShifts[s] == sum(d in days) sum(t in shifts) X[s][d][t];

      /* Consistency definition of AvgShifts (redundancy) */
      AvgShifts == (1/numStudents)*sum(s in students) AssignedShifts[s];

 	  /* Assign each existing shift to only an available student. */
 	  forall(d in days)
 	    forall(t in shifts)
 	      ( sum(s in students) X[s][d][t] ) == Existance[d][t];

      /* Assign a shift to an available student */
 	  forall(d in days)
 	    forall(t in shifts)
 	        forall(s in students)
                X[s][d][t] - Availability[s][d][t]*BigM <= 0;

 	  /* Assign to each student at least the number of shifts defined in MinNumShifts. */
 	  forall(s in students) 
        ( sum(d in days) sum(t in shifts) X[s][d][t] ) >= MinNumShifts[s];
 	  
      /* Assign to each student at most the number of shifts defined in MaxNumShifts. */
 	  forall(s in students) 
        ( sum(d in days) sum(t in shifts) X[s][d][t] ) <= MaxNumShifts[s];
 	  
 	  /* Each student can do at most a certain number of shifts per day */
 	  forall(s in students)
 	    forall(d in days)
 	      ( sum(t in shifts) X[s][d][t] ) <= MaxNumShiftsPerDay;
 }
 
 /***************************************************************************************/
 /*                              OUTPUT	SOLUTION TO STDOUT                              */
 /***************************************************************************************/
 execute { 
 	/* Take final time to compute statistics */
	var after = new Date();
	var elapsed = after.getTime()-temp; 
  
 	/* Write header */
 	writeln("Elapsed time: " + (elapsed/1000) + " seconds\n");
 	writeln("[Info] Begin output");
 	
 	for(var d in thisOplModel.days){
		for(var t in thisOplModel.shifts){
			for(var s in thisOplModel.students){
				if(thisOplModel.X[s][d][t] == 1){
  					writeln(DayNames[d] + "," + ShiftNames[t] + "," + StudNames[s]);
  				}												
 			}						
		} 	 	
 	}
    writeln("");

    writeln("[Info] End output");
}
