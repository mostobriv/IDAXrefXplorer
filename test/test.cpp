int __cdecl main(int argc, const char **argv, const char **envp)
{
  unsigned int v3; // eax
  int v4; // eax
  Dog *v5; // rbx

  v3 = time(0LL);
  srand(v3);
  v4 = rand();
  srand(v4);
  if ( (rand() & 1) != 0 )
  {
    v5 = operator new(8uLL);
    Cat::Cat(v5);
  }
  else
  {
    v5 = operator new(8uLL);
    Dog::Dog(v5);
  }
  v5->vtable->Dog__walk(v5);
  if ( v5 )
    (v5->vtable->Dog__dtor)(v5);
  return 0;
}
