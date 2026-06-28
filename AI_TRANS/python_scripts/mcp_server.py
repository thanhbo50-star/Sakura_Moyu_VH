from mcp.server.fastmcp import FastMCP
import translation_tools

# Initialize FastMCP Server
mcp = FastMCP("ExcelTranslator")

@mcp.tool()
def get_unique_names(file_path: str) -> list[str]:
    """Get all unique character names in the translated Excel file.
    
    Args:
        file_path: Absolute path to the Excel file.
    """
    return translation_tools.get_unique_names(file_path)

@mcp.tool()
def extract_character_lines(file_path: str, character_name: str, keyword: str = "") -> list[dict]:
    """Extract lines spoken by a specific character, optionally filtered by a regex keyword.
    
    Args:
        file_path: Absolute path to the Excel file.
        character_name: Exact name of the character as it appears in the Excel 'name' column. Use 'nan' for uncredited lines/soliloquies.
        keyword: Optional regex to filter the lines by their translation ('trans' column).
    """
    return translation_tools.extract_character_lines(file_path, character_name, keyword)

@mcp.tool()
def apply_text_replacement(file_path: str, character_name: str, target: str, replacement: str, include_nan: bool = True) -> str:
    """Apply a simple text replacement to a character's translated lines.
    
    Args:
        file_path: Absolute path to the Excel file.
        character_name: Name of the character whose lines to modify.
        target: The exact string to be replaced.
        replacement: The string to replace the target with.
        include_nan: If true, also apply replacements to uncredited lines/soliloquies (names that are empty).
    """
    result = translation_tools.apply_text_replacement(file_path, character_name, target, replacement, include_nan)
    return f"Made {result['changes_made']} changes in {file_path} for character {character_name}."

@mcp.tool()
def apply_regex_replacement(file_path: str, character_name: str, pattern: str, replacement: str, include_nan: bool = True) -> str:
    """Apply a regex replacement to a character's translated lines.
    
    Args:
        file_path: Absolute path to the Excel file.
        character_name: Name of the character whose lines to modify.
        pattern: The regular expression pattern to search for in the translations.
        replacement: The string to replace the match with. Can use regex backreferences like \\1.
        include_nan: If true, also apply replacements to uncredited lines/soliloquies (names that are empty).
    """
    result = translation_tools.apply_regex_replacement(file_path, character_name, pattern, replacement, include_nan)
    return f"Made {result['changes_made']} changes in {file_path} for character {character_name}."

if __name__ == "__main__":
    mcp.run()
