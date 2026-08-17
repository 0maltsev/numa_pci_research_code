cmake_minimum_required(VERSION 3.24)

project(numa_pcie_research_benchmark VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Milestone 1 intentionally contains no production implementation. This target
# establishes the language/toolchain contract for later low-latency components.
add_library(numa_pcie_contracts INTERFACE)
target_compile_features(numa_pcie_contracts INTERFACE cxx_std_20)

find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)

enable_testing()
add_test(
  NAME milestone1_contract_validation
  COMMAND "${Python3_EXECUTABLE}" -m unittest discover
          -s "${CMAKE_CURRENT_SOURCE_DIR}/tests"
          -p "test_*.py"
          -v
)
set_tests_properties(
  milestone1_contract_validation
  PROPERTIES ENVIRONMENT
             "PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR};PYTHONDONTWRITEBYTECODE=1"
)

add_custom_target(
  check
  COMMAND "${CMAKE_CTEST_COMMAND}" --output-on-failure
  DEPENDS numa_pcie_contracts
  USES_TERMINAL
)
