engine_o = $(wildcard ../GameEngine/*.o)

my_cpp = $(wildcard *.cpp)
my_o = $(patsubst %.cpp,%.o,$(my_cpp))

out_file = ComplexServer
c_option = -Xlinker -export-dynamic -DLINUX
c_lib_dir = -L/home/share/boost_1_48_0/stage/lib -L../../CLib
c_libs = -lrt -lboost_system-mt-s -lboost_chrono-mt-s -lboost_timer-mt-s -lboost_date_time-mt-s -lboost_thread-mt-s -lboost_regex-mt-s -lpython2.7 -lpthread -ldl -lutil -lmysqlclient

$(out_file) : $(my_o)
	@g++ -o $(out_file) $(engine_o) $(my_o) $(c_option) $(c_lib_dir) $(c_libs)


$(my_o): %.o: %.cpp
	@echo building $< to $@
	@g++ -c -g -DLINUX -I/home/share/boost_1_48_0 -I../../Include $< -o $@

.PHONY : clean
clean :
	@rm -f *.o
	@rm -f $(out_file) 
