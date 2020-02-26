## Menu2Recipe
This program is writen for mapping the menu to the recipe which have ingredients information by text searching of food name.
## Requirements
* Python 
* jieba
* pandas
* xlrd
## Data

    all data are under ./source folder. 
    
  1. Chinese food data: 
        * ./sources/Attribute 
        * ./sources/Menu
        * ./sources/recipe
        * ./Restaurant
  2. Singapore food data:
        * ./Singapore
        
## How to run

python Menu2Recipe.py -n foodname -t 1

Parameters:

|parameter|description|
|---------|-----------|
|-t|foodtype: 1 for Chinese food and 2 for Singapore food|
|-n|foodname: name of food|




