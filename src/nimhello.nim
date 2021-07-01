import strformat

type Person = object
  name: string
  age: int

proc something() =
  let world = "world!"
  var l = @[1,2,3,4,5]
  echo(fmt"Hello, {world}!")
  let p = Person(name: "Devendra Rane", age: 40)
  echo p.name
  echo $l

when isMainModule:
  something()
