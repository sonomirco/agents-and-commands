#!/usr/bin/env python3
"""
Script Extractor Sub-Agent

This sub-agent is part of the Grasshopper Analysis Agent system.
It extracts complete script code from CDATA sections and parameter information
for both C# Script and GhPython Script components.

Task: For all script components identified, extract the complete script code
from CDATA sections. Identify the programming language and any
input/output parameter definitions within the scripts.

Input: XML file path
Output: Complete script extraction with parameters and metadata
"""

import sys
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import re


class ScriptExtractor:
    """
    Extracts script content and parameter information from Grasshopper XML files.
    Handles both C# Script and GhPython Script components.
    """

    def __init__(self, xml_file_path: str):
        self.xml_file_path = xml_file_path
        self.scripts = {}  # GUID -> script info
        self.component_types = {}  # GUID -> component type
        self.libraries = []  # List of libraries used in the definition

    def analyze_xml(self) -> bool:
        """
        Analyze the XML file and extract script components and their code.
        Returns True if successful, False otherwise.
        """
        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()

            # Extract script components
            self._extract_script_components(root)

            # Extract libraries
            self._extract_libraries(root)

            return len(self.scripts) > 0

        except (ET.ParseError, FileNotFoundError, Exception) as e:
            print(f"Error analyzing XML: {e}")
            return False

    def _extract_script_components(self, root):
        """Extract all script components from Grasshopper archive format XML."""
        # Look for DefinitionObjects chunk
        definition_objects = root.find('.//chunk[@name="DefinitionObjects"]')

        if definition_objects is not None:
            # Find all Object chunks
            obj_chunks = definition_objects.findall('.//chunk[@name="Object"]')

            for obj_chunk in obj_chunks:
                self._process_object_chunk(obj_chunk)

    def _extract_libraries(self, root):
        """Extract library information from GHALibraries chunk."""
        # Look for GHALibraries chunk
        gha_libraries = root.find('.//chunk[@name="GHALibraries"]')

        if gha_libraries is not None:
            # Find all Library chunks
            library_chunks = gha_libraries.findall('.//chunk[@name="Library"]')

            for library_chunk in library_chunks:
                library_info = self._extract_library_info(library_chunk)
                if library_info:
                    self.libraries.append(library_info)

    def _extract_library_info(self, library_chunk) -> Optional[Dict]:
        """Extract library information from a Library chunk."""
        items = library_chunk.find('items')
        if items is None:
            return None

        library_info = {
            'name': '',
            'author': '',
            'version': '',
            'assembly_version': '',
            'assembly_full_name': ''
        }

        for item in items.findall('item'):
            item_name = item.get('name')
            if item_name == 'Name' and item.text:
                library_info['name'] = item.text.strip()
            elif item_name == 'Author' and item.text:
                library_info['author'] = item.text.strip()
            elif item_name == 'Version' and item.text:
                library_info['version'] = item.text.strip()
            elif item_name == 'AssemblyVersion' and item.text:
                library_info['assembly_version'] = item.text.strip()
            elif item_name == 'AssemblyFullName' and item.text:
                library_info['assembly_full_name'] = item.text.strip()

        # Return library info if we have at least a name or assembly name
        if library_info['name'] or library_info['assembly_full_name']:
            return library_info
        return None

    def _process_object_chunk(self, object_chunk):
        """Process a single Grasshopper Object chunk to extract script information."""
        # Extract both component type and GUID from the Object chunk
        object_items = object_chunk.find('items')
        component_type_name = None
        component_guid = None

        if object_items is not None:
            for item in object_items.findall('item'):
                if item.get('name') == 'Name' and item.text:
                    component_type_name = item.text.strip()
                elif item.get('name') == 'GUID' and item.text:
                    component_guid = item.text.strip()

        # Skip non-script components (like Scribble, Panel, etc.)
        if component_type_name in ['Scribble', 'Panel', 'Group', 'Sketch']:
            return

        # Use GUID-based detection for script components
        script_type = self._identify_script_type(component_guid, component_type_name)
        if not script_type:
            return

        # Find the Container chunk
        container_chunk = object_chunk.find('.//chunk[@name="Container"]')
        if container_chunk is not None:
            self._process_script_container(container_chunk, script_type)

    def _identify_script_type(self, component_guid: str, component_name: str) -> Optional[str]:
        """
        Identify script component type using GUID-based detection.

        Known GUIDs:
        - C# Script: 7f5c6c55-f846-4a08-9c9a-cfdc285cc6fe
        - GhPython Script: 410755b1-224a-4c1e-a407-bf32fb45ea7e
        - VB.NET Script: 505bb490-8b2d-4056-b655-64c4d4ad61d9 (if needed)
        """
        if not component_guid:
            # Fallback to name-based detection
            if component_name in ['C# Script', 'GhPython Script']:
                return component_name
            return None

        # GUID-based identification (more reliable)
        guid_lower = component_guid.lower()

        if guid_lower == '410755b1-224a-4c1e-a407-bf32fb45ea7e':
            return 'GhPython Script'
        elif guid_lower == '7f5c6c55-f846-4a08-9c9a-cfdc285cc6fe':
            return 'C# Script'
        elif guid_lower == '505bb490-8b2d-4056-b655-64c4d4ad61d9':
            return 'VB.NET Script'

        # Fallback to name-based detection for unknown GUIDs
        if component_name in ['C# Script', 'GhPython Script', 'VB.NET Script']:
            return component_name

        return None

    def _process_script_container(self, container_chunk, component_type_name: str):
        """Process the Container chunk to extract script details."""
        items = container_chunk.find('items')
        if items is None:
            return

        instance_guid = None
        name = None
        nickname = None
        description = None
        code_input = None
        compiled_code = None

        # Extract basic component information
        for item in items.findall('item'):
            item_name = item.get('name')
            if item_name == 'InstanceGuid' and item.text:
                instance_guid = item.text.strip()
            elif item_name == 'Name' and item.text:
                name = item.text.strip()
            elif item_name == 'NickName' and item.text:
                nickname = item.text.strip()
            elif item_name == 'Description' and item.text:
                description = item.text.strip()
            elif item_name == 'CodeInput' and item.text:
                code_input = item.text.strip()
            elif item_name == 'CompiledCode' and item.text:
                # For C# scripts, code might be in CDATA within CompiledCode
                compiled_code = item.text.strip()

        if instance_guid:
            self.component_types[instance_guid] = component_type_name

            # Extract parameters
            input_params = self._extract_input_parameters(container_chunk)
            output_params = self._extract_output_parameters(container_chunk)

            # Determine the actual script code
            script_code = self._extract_script_code(code_input, compiled_code, component_type_name)

            self.scripts[instance_guid] = {
                'component_type': component_type_name,
                'instance_guid': instance_guid,
                'name': name or '',
                'nickname': nickname or '',
                'description': description or '',
                'script_code': script_code,
                'language': self._determine_language(component_type_name),
                'input_parameters': input_params,
                'output_parameters': output_params,
                'display_name': nickname or name or f"{component_type_name}_{instance_guid[:8]}"
            }

    def _extract_script_code(self, code_input: Optional[str], compiled_code: Optional[str], component_type: str) -> str:
        """Extract the actual script code from various sources."""
        if component_type == 'GhPython Script':
            # For Python scripts, code is typically in CodeInput
            return code_input or ''
        elif component_type == 'C# Script':
            # For C# scripts, check both CodeInput and CompiledCode
            # CompiledCode might contain CDATA with the actual source
            if code_input:
                return code_input
            elif compiled_code:
                # Try to extract from CDATA if present
                cdata_match = re.search(r'<!\[CDATA\[(.*?)\]\]>', compiled_code, re.DOTALL)
                if cdata_match:
                    return cdata_match.group(1).strip()
                return compiled_code

        return code_input or compiled_code or ''

    def _determine_language(self, component_type: str) -> str:
        """Determine the programming language based on component type."""
        if component_type == 'C# Script':
            return 'C#'
        elif component_type == 'GhPython Script':
            return 'Python'
        return 'Unknown'

    def _extract_input_parameters(self, container_chunk) -> List[Dict]:
        """Extract input parameter information from InputParam chunks."""
        input_params = []

        # Look for ParameterData chunk which contains InputParam chunks
        param_data_chunk = container_chunk.find('.//chunk[@name="ParameterData"]')
        if param_data_chunk is not None:
            input_param_chunks = param_data_chunk.findall('.//chunk[@name="InputParam"]')

            for input_chunk in input_param_chunks:
                param_info = self._extract_parameter_info(input_chunk)
                if param_info:
                    input_params.append(param_info)

        return input_params

    def _extract_output_parameters(self, container_chunk) -> List[Dict]:
        """Extract output parameter information from OutputParam chunks."""
        output_params = []

        # Look for ParameterData chunk which contains OutputParam chunks
        param_data_chunk = container_chunk.find('.//chunk[@name="ParameterData"]')
        if param_data_chunk is not None:
            output_param_chunks = param_data_chunk.findall('.//chunk[@name="OutputParam"]')

            for output_chunk in output_param_chunks:
                param_info = self._extract_parameter_info(output_chunk)
                if param_info:
                    output_params.append(param_info)

        return output_params

    def _extract_parameter_info(self, param_chunk) -> Optional[Dict]:
        """Extract parameter information from a parameter chunk."""
        items = param_chunk.find('items')
        if items is None:
            return None

        param_info = {
            'name': '',
            'nickname': '',
            'description': '',
            'type': '',
            'access': 'item',
            'optional': False,
            'instance_guid': ''
        }

        for item in items.findall('item'):
            item_name = item.get('name')
            if item_name == 'Name' and item.text:
                param_info['name'] = item.text.strip()
            elif item_name == 'NickName' and item.text:
                param_info['nickname'] = item.text.strip()
            elif item_name == 'Description' and item.text:
                param_info['description'] = item.text.strip()
            elif item_name == 'InstanceGuid' and item.text:
                param_info['instance_guid'] = item.text.strip()
            elif item_name == 'Optional' and item.text:
                param_info['optional'] = item.text.strip().lower() == 'true'
            elif item_name == 'Access' and item.text:
                # Convert access number to readable format
                access_num = item.text.strip()
                access_map = {'0': 'item', '1': 'list', '2': 'tree'}
                param_info['access'] = access_map.get(access_num, 'item')

        # Only return if we have meaningful information
        if param_info['name'] or param_info['nickname']:
            return param_info
        return None

    def generate_script_analysis(self) -> str:
        """Generate the script analysis output."""
        if not self.scripts:
            return "No script components found in the XML file."

        output = []

        # Header
        output.append("# Script Analysis")
        output.append("")
        output.append(f"**File:** {os.path.basename(self.xml_file_path)}")
        output.append(f"**Script Components:** {len(self.scripts)}")
        if self.libraries:
            output.append(f"**Libraries Used:** {len(self.libraries)}")
        output.append("")

        # Libraries section
        if self.libraries:
            output.append("## Libraries and Dependencies")
            output.append("")

            # Deduplicate libraries
            unique_libraries = set()
            for library in self.libraries:
                if library['name'] and library['name'].strip():
                    unique_libraries.add(library['name'].strip())
                elif library['assembly_full_name']:
                    # Extract name from assembly full name
                    assembly_name = library['assembly_full_name'].split(',')[0].strip()
                    unique_libraries.add(assembly_name)

            for lib_name in sorted(unique_libraries):
                output.append(f"- {lib_name}")
            output.append("")

        # Group scripts by type
        csharp_scripts = [s for s in self.scripts.values() if s['language'] == 'C#']
        python_scripts = [s for s in self.scripts.values() if s['language'] == 'Python']

        if csharp_scripts:
            output.append(f"## C# Script Components ({len(csharp_scripts)})")
            output.append("")
            for script in csharp_scripts:
                self._add_script_details(output, script)
                output.append("")

        if python_scripts:
            output.append(f"## GhPython Script Components ({len(python_scripts)})")
            output.append("")
            for script in python_scripts:
                self._add_script_details(output, script)
                output.append("")

        # Summary
        output.append("## Script Summary")
        output.append("")
        output.append(f"- **Total Scripts:** {len(self.scripts)}")
        output.append(f"- **C# Scripts:** {len(csharp_scripts)}")
        output.append(f"- **Python Scripts:** {len(python_scripts)}")

        total_inputs = sum(len(s['input_parameters']) for s in self.scripts.values())
        total_outputs = sum(len(s['output_parameters']) for s in self.scripts.values())
        output.append(f"- **Total Input Parameters:** {total_inputs}")
        output.append(f"- **Total Output Parameters:** {total_outputs}")

        return "\n".join(output)

    def _add_script_details(self, output: List[str], script: Dict):
        """Add detailed script information to output."""
        output.append(f"### {script['display_name']}")
        output.append(f"**GUID:** `{script['instance_guid']}`")
        output.append(f"**Language:** {script['language']}")

        if script['description']:
            output.append(f"**Description:** {script['description']}")

        # Input parameters
        if script['input_parameters']:
            output.append("**Input Parameters:**")
            for param in script['input_parameters']:
                param_name = param['nickname'] or param['name']
                access_str = f" ({param['access']})" if param['access'] != 'item' else ""
                optional_str = " [Optional]" if param['optional'] else ""
                output.append(f"- `{param_name}`: {param['description']}{access_str}{optional_str}")
        else:
            output.append("**Input Parameters:** None")

        # Output parameters
        if script['output_parameters']:
            output.append("**Output Parameters:**")
            for param in script['output_parameters']:
                param_name = param['nickname'] or param['name']
                output.append(f"- `{param_name}`: {param['description']}")
        else:
            output.append("**Output Parameters:** None")

        # Script code
        if script['script_code']:
            output.append("**Script Code:**")
            output.append("```" + script['language'].lower())
            output.append(script['script_code'])
            output.append("```")
        else:
            output.append("**Script Code:** [Empty or not found]")


def main():
    """Main entry point for the script extractor sub-agent."""
    if len(sys.argv) != 2:
        print("Usage: python script_extractor.py <xml_file_path>")
        print("")
        print("This sub-agent extracts script code and parameter information")
        print("from both C# Script and GhPython Script components in Grasshopper XML files.")
        sys.exit(1)

    xml_file_path = sys.argv[1]

    # Validate input file
    if not os.path.exists(xml_file_path):
        print(f"Error: File not found: {xml_file_path}")
        sys.exit(1)

    file_ext = xml_file_path.lower()
    if file_ext.endswith('.gh'):
        print(f"Error: Binary .gh files are not supported. Please save your Grasshopper definition as .ghx format and try again.")
        sys.exit(1)
    if not (file_ext.endswith('.xml') or file_ext.endswith('.ghx')):
        print(f"Warning: File does not have a supported XML extension (.xml or .ghx): {xml_file_path}")
        print("Proceeding anyway, but analysis may fail if the file is not in XML format.")

    # Create and run the extractor
    extractor = ScriptExtractor(xml_file_path)

    if not extractor.analyze_xml():
        print("Error: Failed to analyze XML file or no script components found")
        sys.exit(1)

    # Generate and output the script analysis
    script_analysis = extractor.generate_script_analysis()
    print(script_analysis)


if __name__ == "__main__":
    main()