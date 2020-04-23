# Wikipedia map

The goal of this project is to create a map of the wikipedia articles and how they are linked together.

## External Dependancies:
- libxml2
- libxslt

## Todo
- [x] Wikipedia web scraping
- [x] Find a way to store extracted data
- [x] Merge WikipediaMap and Page respectively with Graph and Vertex -> data structure is transparent from the user and well encapsulated
- [x] Parallelize the mapping -> created custom threads for both get requests and data processing
- [ ] Generate the map
- [ ] _LATE_ Create a web application to visualize easily the map

## Main issues
- [ ] run the program on multiple processes but things can begin very complicated since I have to share a variable between processes.
- [X] get node by page name seems to be in O(n) so the algorithm gets slower by adding more pages -> solved by using a lookup table which registers nodes by page\_name attribute.
- [x] very poor performance -> currently making a performance analyser

