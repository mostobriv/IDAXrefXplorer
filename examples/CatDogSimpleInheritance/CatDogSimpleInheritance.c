// g++ CatDogSimpleInheritance.c -o CatNDog


#include <cstdlib>
#include <iostream>
#include <ctime>

#include "CatDogSimpleInheritance.h"

int main() {
    Mammal *m;
    std::srand(std::time(nullptr));
    std::srand(std::rand());

    if (std::rand() % 2) {
        m = new Cat();
    } else {
        m = new Dog();
    }
    m->walk();

    delete m;
}
