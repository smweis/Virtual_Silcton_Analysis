#install.packages("BiDimRegression")
library("BiDimRegression", lib.loc="~/R/win-library/3.1")


#WHERE IS THE DATA?
#setwd("C:/Users/stweis/Desktop")

observations <- 4                 #Number of observation per participant
participants <- 1                 #Number of participants


#Load Data into R - Type in name of data file here (must be DV1|DV2|IV1|IV2). 
#as written, save your data (in Excel) as a CSV. Alternatively, "Import Dataset", then change to the line below
#data <- read.csv("Sample_Bidi.csv", header=FALSE)   
data <- data.frame(raw_model_building)

colnames(data) <- c("depV1","depV2","indepV1","indepV2")
results <- data.frame()



for (i in 1:(observations*participants)){ 
  
  if (i%%observations==0){ 
    
    temp_results <- BiDimRegression(data[c((i-(observations-1)):i),])

    results[i/observations,1] <- as.character(i/observations)
    results[i/observations,2] <- temp_results$euclidean.r
    results[i/observations,3] <- temp_results$euclidean.rsqr
    #results[i/observations,4] <- temp_results$ ANYTHING ELSE YOU WANT - But be sure to add them to the colnames below.
    #results[i/observations,5] <- temp_results$ ANYTHING ELSE YOU WANT

}
}

colnames(results) <- c('Participant_Number','Euclidean_R','Euclidean_R2')#name other Cols if you add them in above
rm(i,observations,participants,temp_results)#removes temporary files
