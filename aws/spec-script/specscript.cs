using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

public class SpecScriptSection
{
    public string Type { get; set; }
    public string Title { get; set; }
    public List<SpecScriptContent> Content { get; set; } = new List<SpecScriptContent>();
}

public class SpecScriptContent
{
    public string ContentType { get; set; } // "kv", "step", "list"
    public string Key { get; set; }
    public string Value { get; set; }
    public string Text { get; set; }
}

public class SpecScriptParser
{
    public List<SpecScriptSection> Sections { get; set; } = new List<SpecScriptSection>();

    public void Parse(IEnumerable<string> lines)
    {
        SpecScriptSection currentSection = null;

        foreach (var rawLine in lines)
        {
            var line = rawLine.TrimEnd('\n', '\r');
            if (string.IsNullOrWhiteSpace(line) || line.TrimStart().StartsWith("#"))
                continue;

            var indent = line.Length - line.TrimStart(' ').Length;
            var content = line.TrimStart(' ');

            // Section header
            if (content.StartsWith("@"))
            {
                if (currentSection != null)
                    Sections.Add(currentSection);

                var match = Regex.Match(content, @"@(\w+)(?:\s+(.+))?");
                if (match.Success)
                {
                    currentSection = new SpecScriptSection
                    {
                        Type = match.Groups[1].Value,
                        Title = match.Groups[2].Success ? match.Groups[2].Value : null
                    };
                }
                continue;
            }

            // Inside a section
            if (currentSection != null)
            {
                // Key-value pair
                if (content.Contains(":"))
                {
                    var idx = content.IndexOf(':');
                    var key = content.Substring(0, idx).Trim();
                    var value = content.Substring(idx + 1).Trim();
                    currentSection.Content.Add(new SpecScriptContent
                    {
                        ContentType = "kv",
                        Key = key,
                        Value = value
                    });
                }
                // Numbered step
                else if (Regex.IsMatch(content, @"^\d+\.\s"))
                {
                    currentSection.Content.Add(new SpecScriptContent
                    {
                        ContentType = "step",
                        Text = content
                    });
                }
                // List item
                else
                {
                    currentSection.Content.Add(new SpecScriptContent
                    {
                        ContentType = "list",
                        Text = content
                    });
                }
            }
        }

        if (currentSection != null)
            Sections.Add(currentSection);
    }

    // Example: Convert to a structured dictionary-like object
    public Dictionary<string, List<Dictionary<string, object>>> ToStructured()
    {
        var result = new Dictionary<string, List<Dictionary<string, object>>>();

        foreach (var section in Sections)
        {
            var secType = section.Type;
            var secTitle = section.Title;
            var content = section.Content;

            var parsedContent = ParseContent(content);
            if (!result.ContainsKey(secType))
                result[secType] = new List<Dictionary<string, object>>();

            if (!string.IsNullOrEmpty(secTitle))
            {
                var dict = new Dictionary<string, object> { { "title", secTitle } };
                foreach (var kv in parsedContent)
                    dict[kv.Key] = kv.Value;
                result[secType].Add(dict);
            }
            else
            {
                result[secType].Add(parsedContent);
            }
        }
        return result;
    }

    private Dictionary<string, object> ParseContent(List<SpecScriptContent> content)
    {
        var result = new Dictionary<string, object>();
        var steps = new List<string>();
        var items = new List<string>();

        foreach (var item in content)
        {
            if (item.ContentType == "kv")
            {
                if (item.Value.Contains(","))
                {
                    var values = item.Value.Split(',').Select(v => v.Trim()).ToList();
                    result[item.Key] = values;
                }
                else
                {
                    result[item.Key] = item.Value;
                }
            }
            else if (item.ContentType == "step")
            {
                steps.Add(item.Text);
            }
            else if (item.ContentType == "list")
            {
                items.Add(item.Text);
            }
        }
        if (steps.Count > 0)
            result["steps"] = steps;
        if (items.Count > 0)
            result["items"] = items;
        return result;
    }
}

class Program
{
    static void Main()
    {
        var specscript = @"
@meta
  Title: User Authentication Module
  Version: 1.0
  Author: Jane Doe
  Date: 2024-06-15

@entity User
  id: UUID, required, unique
  email: string, required, unique
  password_hash: string, required

@usecase RegisterUser
  Description: Allows a new user to create an account.
  Input: email (string), password (string)
  Output: user_id (UUID)
  Steps:
    1. Validate email format
    2. Check if email is unique
    3. Hash password
    4. Create user record
    5. Return user_id

@constraint
  Password must be at least 8 characters.
  Email must be unique.
";

        var parser = new SpecScriptParser();
        parser.Parse(specscript.Split('\n'));

        var structured = parser.ToStructured();

        // Print result
        foreach (var sectionType in structured.Keys)
        {
            Console.WriteLine($"Section: {sectionType}");
            foreach (var section in structured[sectionType])
            {
                foreach (var kv in section)
                {
                    if (kv.Value is List<string> list)
                    {
                        Console.WriteLine($"  {kv.Key}:");
                        foreach (var item in list)
                            Console.WriteLine($"    - {item}");
                    }
                    else if (kv.Value is List<object> objList)
                    {
                        Console.WriteLine($"  {kv.Key}: {string.Join(", ", objList)}");
                    }
                    else
                    {
                        Console.WriteLine($"  {kv.Key}: {kv.Value}");
                    }
                }
            }
        }
    }
}