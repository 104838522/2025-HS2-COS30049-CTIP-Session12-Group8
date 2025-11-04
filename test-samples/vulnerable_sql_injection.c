// Vulnerable: SQL injection (simulated)
#include <stdio.h>
#include <string.h>

void executeQuery(char *username) {
    char query[256];
    
    // Vulnerable: direct string concatenation
    sprintf(query, "SELECT * FROM users WHERE name = '%s'", username);
    
    printf("Executing: %s\n", query);
    // In real code, this would execute the query
}

int main() {
    char username[100];
    
    printf("Enter username: ");
    scanf("%99s", username);
    
    executeQuery(username);
    
    return 0;
}
