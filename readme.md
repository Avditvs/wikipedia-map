# Wikipedia map

The goal of this project is to create a map of the wikipedia articles and how they are linked together.

## External Dependancies:
- libxml2
- libxslt

## Todo
- [x] Wikipedia web scraping
- [x] Find a way to store extracted data
- [ ] Parallelize the mapping
- [ ] In background, prefetch and parse pages
- [ ] Generate the map
- [ ] Create a web application to visualize easily the map

## Main issues
- [X] get node by page name seems to be in O(n) so the algorithm gets slower by adding more pages -> solved by using a lookup table which registers nodes by page\_name attribute.
- [x] very poor performance -> currently making a performance analyser

