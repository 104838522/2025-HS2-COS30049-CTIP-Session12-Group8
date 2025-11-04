// Safe: Integer overflow protection
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

int main() {
    unsigned int size;
    char *buffer;
    
    printf("Enter buffer size: ");
    scanf("%u", &size);
    
    // Check for overflow before allocation
    if (size > UINT_MAX - 1) {
        fprintf(stderr, "Size too large\n");
        return 1;
    }
    
    buffer = (char *)malloc(size + 1);
    
    if (buffer) {
        memset(buffer, 'A', size);
        buffer[size] = '\0';
        free(buffer);
    }
    
    return 0;
}
