<Query Kind="Program" />

static void Main()
{
	string filename = @"C:\Users\cgdil\Documents\Files\Programming Stuff\Rust\AdventOfCode2018\input\day4.txt";
	
	Console.WriteLine(
        System.IO.File.ReadAllLines(filename)
              .OrderBy((line) => line)
              .Select((line) => Regex.Match(line, @"^.*:(\d{2})] (.*)$"))
              .Select((match) => new {minute = int.Parse(match.Groups[1].Value), command = match.Groups[2].Value})
              .Aggregate(new {curr_id = 0, commands = new[] {new {id = 0, minute = 0, command = "none", prev_minute = 0}}.AsEnumerable(), last_minute = 0},
                         (info, ev) => new
                                       {
                                           curr_id = ev.command.Contains("#") ? int.Parse(Regex.Match(ev.command, @"#(\d+)").Groups[1].Value) : info.curr_id,
                                           commands = info.commands.Concat(new[] {new {id = info.curr_id, minute = ev.minute, command = ev.command, prev_minute = info.last_minute}}),
                                           last_minute = ev.minute
                                       })
              .commands
              .Where((command) => command.command.StartsWith("wake"))
              .GroupBy((command) => command.id,
                       (command) => Enumerable.Range(command.prev_minute, command.minute - command.prev_minute))
              .Select((group) => new
                                 {
                                     id = group.Key,
                                     minute = group.SelectMany((x) => x)
                                                   .GroupBy((minute) => minute)
                                                   .Aggregate(new {minute = 0, count = 0},
                                                              (max, minuteGroup) => minuteGroup.Count() > max.count
                                                                                        ? new {minute = minuteGroup.Key, count = minuteGroup.Count()}
                                                                                        : max)
                                 })
              .OrderByDescending((group) => group.minute.count)
              .Take(1)
              .Aggregate("", (_, result) => string.Format("Guard #{0} was asleep the most on a particular minute.  On minute {1}, the guard was asleep {2} times.\n" +
                                                          "The solution to problem 4.1 is: {3}",
                                                          result.id, result.minute.minute, result.minute.count, result.id * result.minute.minute)));
}

// Define other methods and classes here