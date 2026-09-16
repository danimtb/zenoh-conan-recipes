cmake_minimum_required(VERSION 3.16)
project(test_package LANGUAGES CXX)

find_package(zenohcpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cxx)
if(TARGET zenohcxx::zenohc)
    target_link_libraries(${PROJECT_NAME} PRIVATE zenohcxx::zenohc)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE zenohcxx::zenohpico)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
