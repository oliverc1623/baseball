#
# This is a Shiny web application. You can run the application by clicking
# the 'Run App' button above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

library(shiny)
library(Lahman)
library(tidyverse)
library(stringi)
data(Pitching)
data(People)

clean_people <- People %>% select(playerID, birthYear, birthCountry, deathYear, nameFirst, nameLast, weight, height, bats, throws) %>% 
    mutate(fullname = tolower(paste(nameFirst,nameLast))) %>% 
    select(-nameFirst, -nameLast)

search_player <- function(name){
    search_res <- grepl(tolower(name), clean_people$fullname)
    indx <- which(search_res)
    return(indx)
}

# Define UI for application that draws a histogram
ui <- fluidPage(

    # Application title
    titlePanel("Pitcher Comparer"),

    # Sidebar with a slider input for number of bins 
    sidebarLayout(
        sidebarPanel(
            textInput("text", label = h3("Search Pitcher"), value = "Enter name..."),
            actionButton("action", label = "Search"),
        ),

        # Show a plot of the generated distribution
        mainPanel(
            plotOutput('plot1')
        )
    )
)

# Define server logic required to draw a histogram
server <- function(input, output) {
    v <- reactiveValues(data = NULL)
    pitcher_df <- eventReactive(input$action, {
        single_player <- clean_people[search_player(input$text),]
        single_id <- single_player$playerID
        v$data <- single_id
        pitcher_df <- Pitching %>% filter(playerID == single_id)
        pitcher_df
    })
    
    output$plot1 <- renderPlot({
        year_span <- pitcher_df()$yearID
        games_started <- pitcher_df()$GS
        firstName <- People$nameFirst[People$playerID == v$data]
        lastName <- People$nameLast[People$playerID == v$data]
        if(sum(pitcher_df()$GS) == 0 && sum(pitcher_df()$SV > 0)){
            ranged_df <- Pitching %>% 
                filter(yearID >= min(year_span), yearID <= max(year_span), ERA <= 10, ERA > 0) 
            ranged_df %>% filter(SV > round(mean(ranged_df$SV))) %>% 
                ggplot() + 
                geom_boxplot(aes(as.factor(yearID), ERA, fill=lgID)) + 
                geom_jitter(aes(x=as.factor(yearID), ERA), color="black", size=.1, width = 0.2) + 
                geom_point(aes(x=as.factor(yearID), ERA), color="blue", data = pitcher_df(), size=3) + 
                ggtitle(paste(firstName, lastName, "vs Rest of MLB")) +
                xlab("Year") + 
                labs(fill='League')
        } else {
            ranged_df <- Pitching %>% 
                filter(yearID >= min(year_span), yearID <= max(year_span), ERA <= 10, ERA > 0) 
            ranged_df %>% filter(GS > round(mean(ranged_df$GS))) %>%
                ggplot() + 
                geom_boxplot(aes(as.factor(yearID), ERA, fill=lgID)) + 
                geom_point(aes(x=as.factor(yearID), ERA), color="blue", data = pitcher_df(), size=3) + 
                ggtitle(paste(firstName, lastName, "vs Rest of MLB")) +
                xlab("Year") + 
                labs(fill='League')
        }
    })
}

# Run the application 
shinyApp(ui = ui, server = server)
