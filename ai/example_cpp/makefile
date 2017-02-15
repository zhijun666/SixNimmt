srcFiles=exampleai.cpp jsoncpp.o
exampleaicpp : $(srcFiles)
	g++ -o exampleaicpp -I../../libs -std=c++11 $(srcFiles) 
jsoncpp.o : ../../libs/jsoncpp.cpp
	g++ -c ../../libs/jsoncpp.cpp -std=c++11 -o jsoncpp.o
clean:
	rm exampleaicpp *.o
