engine_cpp = $(wildcard *.cpp)
engine_o = $(patsubst %.cpp,%.o,$(engine_cpp))

.PHONY : complite
complite : $(engine_o)

$(engine_o): %.o: %.cpp
	@echo building $< to $@
	@g++ -c -g -DLINUX -I/home/share/boost_1_48_0 -I../../Include $< -o $@

.PHONY : clean
clean :
	@rm -f *.o

