// Vulnerable: Integer overflow leading to buffer overflow
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    unsigned int size;
    char *buffer;
    
    printf("Enter buffer size: ");
    scanf("%u", &size);
    
    // Vulnerable: size + 1 can overflow
    buffer = (char *)malloc(size + 1);
    
    if (buffer) {
        memset(buffer, 'A', size);
        buffer[size] = '\0';
        free(buffer);
    }
    
    return 0;
}
