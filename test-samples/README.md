# Test Samples for VulnLocator

This directory contains sample C/C++ code files for testing the vulnerability detection system.

## Vulnerable Examples

1. **vulnerable_buffer_overflow.c** - Buffer overflow using `gets()` and `strcpy()`
2. **vulnerable_format_string.c** - Format string vulnerability
3. **vulnerable_integer_overflow.c** - Integer overflow leading to buffer overflow
4. **vulnerable_use_after_free.cpp** - Use-after-free memory error
5. **vulnerable_sql_injection.c** - SQL injection vulnerability (simulated)
6. **vulnerable_null_pointer.cpp** - Null pointer dereference

## Safe Examples

1. **safe_buffer_handling.c** - Proper bounds checking with `fgets()` and `strncpy()`
2. **safe_format_string.c** - Safe format string usage
3. **safe_integer_handling.c** - Integer overflow protection
4. **safe_memory_management.cpp** - Smart pointers for memory safety
5. **safe_parameterized_query.c** - Input validation and parameterized queries
6. **safe_null_check.cpp** - Proper null pointer checking

## Usage

Use these files to test your VulnLocator application by:
1. Copying the code from vulnerable files to test detection
2. Copying the code from safe files to verify no false positives
3. Comparing the analysis results between vulnerable and safe versions

## Common Vulnerabilities Demonstrated

- **CWE-120**: Buffer Copy without Checking Size of Input
- **CWE-134**: Use of Externally-Controlled Format String
- **CWE-190**: Integer Overflow or Wraparound
- **CWE-416**: Use After Free
- **CWE-89**: SQL Injection
- **CWE-476**: NULL Pointer Dereference
