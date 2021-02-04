# To use this script, open the file in R. 

# You'll need to install the BiDimRegression package:
#install.packages("BiDimRegression")

silctonBidi <- function(pathToData,pathToTemplate) {

  # Take a path to data: ./sampleBidiData.csv
  # And a path to the templateData: ./modelBuildingTemplate.csv
  
  # Output the scored bidimensional regression data.
  
  
  # Your model building data from the Virtual Silcton website
  data <- read.csv(pathToData)   
  # The template, which can be downloaded from 
  # https://github.com/smweis/Virtual_Silcton_Analysis
  templateData <- read.csv(pathToTemplate)
  
  # There's a specified order to make sure the buildings line up in their respective routes.
  buildingOrder <- c('Batty House','Lynch Station','Harris Hall','Harvey House',
                     'Golledge Hall','Snow Church','Sauer Center','Tobler Museum')
  
  # Sort the buildings in the template and data by that order.
  data <- data[order(data$participant,factor(data$building, levels = buildingOrder)), ]
  templateData <- templateData[order(factor(templateData$building, levels = buildingOrder)), ]
  
  # Rename and initialize a few variables
  data$depV1 <- data$x
  data$depV2 <- data$y
  results <- data.frame()
  
  # 8 buildings for Silcton. This will do the overall and within-route model building calculations.
  observations <- 8
  participants <- nrow(data)/observations
  
  # Loop through each participant's data set, run it through the bidimensional regression,
  # Save the data to the results. 
  for (i in 1:(observations*participants)){ 
    
    if (i%%observations==0){ 
      
      # Select the data to be analyzed
      tempData <- data[c((i-(observations-1)):i),]
      id <- tempData[1,'participant']
      tempData <- tempData[,c(8,9)]
      tempData$indepV1 <- templateData$indepV1
      tempData$indepV2 <- templateData$indepV2
      
      temp_results <- BiDimRegression(tempData)
  
      results[i/observations,'participant'] <- as.character(id)
      results[i/observations,'Overall_r'] <- temp_results$euclidean.r
      results[i/observations,'Overall_rsquared'] <- temp_results$euclidean.rsqr
      results[i/observations,'Overall_angle'] <- temp_results$euclidean.angleDEG
      results[i/observations,'Overall_x_scale'] <- temp_results$euclidean.scaleFactorX
      results[i/observations,'Overall_y_scale'] <- temp_results$euclidean.scaleFactorY
      results[i/observations,'Overall_distortion_index'] <- temp_results$euclidean.diABSqr
      
      tempDataBatty <- tempData[c(1:4),]
      tempDataGolledge <- tempData[c(5:8),]
      
      temp_resultsBatty <- BiDimRegression(tempDataBatty)
      temp_resultsGolledge <- BiDimRegression(tempDataGolledge)
      
      results[i/observations,'Batty_r'] <- temp_resultsBatty$euclidean.r
      results[i/observations,'Batty_rsquared'] <- temp_resultsBatty$euclidean.rsqr
      results[i/observations,'Batty_angle'] <- temp_resultsBatty$euclidean.angleDEG
      results[i/observations,'Batty_x_scale'] <- temp_resultsBatty$euclidean.scaleFactorX
      results[i/observations,'Batty_y_scale'] <- temp_resultsBatty$euclidean.scaleFactorY
      results[i/observations,'Batty_distortion_index'] <- temp_resultsBatty$euclidean.diABSqr
      
      results[i/observations,'Golledge_r'] <- temp_resultsGolledge$euclidean.r
      results[i/observations,'Golledge_rsquared'] <- temp_resultsGolledge$euclidean.rsqr
      results[i/observations,'Golledge_angle'] <- temp_resultsGolledge$euclidean.angleDEG
      results[i/observations,'Golledge_x_scale'] <- temp_resultsGolledge$euclidean.scaleFactorX
      results[i/observations,'Golledge_y_scale'] <- temp_resultsGolledge$euclidean.scaleFactorY
      results[i/observations,'Golledge_distortion_index'] <- temp_resultsGolledge$euclidean.diABSqr
      
  }
  }
  
  write.csv(results,".\\silctonBidiOut.csv", row.names = FALSE)
return(results)

}

# DEMO:
# library(BiDimRegression)
# results <- silctonBidi('./sampleBidiData.csv','modelBuildingTemplate.csv')
