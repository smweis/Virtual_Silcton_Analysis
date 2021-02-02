library("BiDimRegression", lib.loc="~/R/win-library/3.0")

#Data in format: depV1 depV2 indepV1 indepV2
#Name Dataset -> Data
UIinput <- function(){
  
  #Ask for user input
  x <- readline(prompt = "How many data points per participant? ")
  
  #Return

  
  y <- readline(prompt = "How many participants? ")
  
  return(x)
  return(y)
}

UIinput()

data(NakayaData)

resultsBiDimRegr <- BiDimRegression(NakayaData)

print(resultsBiDimRegr)

LL <- lapply(1:x, 
             function(i) {
               T <- as.Date(as.mondate (STARTLISTING)+i)
               DELIST <- (subset(datensatz_Start_End.frame, TIME <= T))[,1]
               assign(paste('b',i,sep=''),DELIST) 
             }
)


result <- do.call(rbind, LL)
