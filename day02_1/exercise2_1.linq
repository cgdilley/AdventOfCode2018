<Query Kind="Program" />

void Main()
{
	Console.WriteLine(
	  System.IO.File.ReadAllLines(@"C:\Users\cgdil\Documents\Files\Programming Stuff\Rust\AdventOfCode2018\input\day2.txt")
	  .SelectMany((line) => Enumerable.Range(0, line.Length)
					              .Select((i) => new {subString = line.Remove(i, 1), i = i})
								  .GroupBy((info) => info.subString,
								           (info) => info.i))
	  .GroupBy((group) => group.Key,
	           (group) => group,
			   (key, results) => new {Key = key, positions = results.SelectMany(x => x)})	  
	  .Where((group) => group.positions.GroupBy(i => i).Any((count) => count.Count() > 1))
	  .Aggregate("", (agg, results) => agg + results.Key + " "));
}

// Define other methods and classes here
