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
 int numShifts	 = ...; /* Number of shifts per day, the maximum value */

 /* Define helping variable "big M" */
 int BigM        = 1000;

 /* Define ranges according to the parameters */
 range students = 1..numStudents;
 range days 	= 1..numDays;
 range shifts 	= 1..numShifts;
 
 /* Declare strings for student and day names (e.g. "Luigi Berducci", "Mon 01 Dec", ...)*/
 string StudNames[students] = ...;
 string DayNames[days] 		= ...;
 
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
 
 /* OBJECTIVE FUNCTION */
 /* Minimize the total number of assignment. 
 	Note: This objective function is mandatory to avoid multiple assignment of the same shift.
 	Otherwise we should add a constraint to unicity of assignment 
 	but with this function is implicitly modeled. */
 minimize sum(s in students) sum(d in days) sum(t in shifts) X[s][d][t];
 
 /* CONSTRAINTS */
 subject to {
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
 	  
 	  /* Each student can do at most one shift per day */
 	  forall(s in students)
 	    forall(d in days)
 	      ( sum(t in shifts) X[s][d][t] ) <= 1;
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
  					writeln(DayNames[d] + "," + t + "," + StudNames[s]);
  				}												
 			}						
		} 	 	
 	}
    writeln("");

    writeln("[Info] End output");
}
