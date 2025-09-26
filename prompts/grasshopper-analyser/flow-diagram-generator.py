#!/usr/bin/env python3
"""
Flow Diagram Generator Sub-Agent

This sub-agent is part of the Grasshopper Analysis Agent system.
It takes connection mapping data and creates text-based flow diagrams
showing how components connect, with focus on main workflow paths
and branching/parallel processing.

Task: Using the connection mapping data, create a text-based flow diagram
showing how components connect. Identify the main workflow paths and any
branching or parallel processing.

Input: XML file path
Output: Text-based flow diagrams using arrows (---> format)
"""

import sys
import os
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Optional
import re


class FlowDiagramGenerator:
    """
    Generates text-based flow diagrams from Grasshopper XML connection data.
    """

    def __init__(self, xml_file_path: str):
        self.xml_file_path = xml_file_path
        self.components = {}  # GUID -> component info
        self.connections = defaultdict(list)  # source_guid -> [target_guids]
        self.reverse_connections = defaultdict(list)  # target_guid -> [source_guids]

    def analyze_xml(self) -> bool:
        """
        Analyze the XML file and extract component and connection information.
        Returns True if successful, False otherwise.
        """
        try:
            tree = ET.parse(self.xml_file_path)
            root = tree.getroot()

            # Extract components
            self._extract_components(root)

            # Extract connections
            self._extract_connections(root)

            return len(self.components) > 0

        except (ET.ParseError, FileNotFoundError, Exception) as e:
            print(f"Error analyzing XML: {e}")
            return False

    def _extract_components(self, root):
        """Extract all components from Grasshopper archive format XML."""
        # Look for DefinitionObjects chunk using correct Grasshopper archive format
        definition_objects = root.find('.//chunk[@name="DefinitionObjects"]')

        if definition_objects is not None:
            # Find all Object chunks - these represent actual Grasshopper components
            obj_chunks = definition_objects.findall('.//chunk[@name="Object"]')

            for i, obj_chunk in enumerate(obj_chunks):
                self._process_grasshopper_object_chunk(obj_chunk, i)

        # Fallback: look for components with InstanceGuid in any element
        if not self.components:
            print("Debug: No components found in chunks, trying fallback...")
            for elem in root.iter():
                instance_guid = elem.get('InstanceGuid')
                if instance_guid:
                    print(f"Debug: Found component with GUID: {instance_guid[:8]}...")
                    display_name = (
                        elem.get('NickName') or
                        elem.get('Name') or
                        elem.tag or
                        f"Component_{instance_guid[:8]}"
                    ).strip()

                    self.components[instance_guid] = {
                        'display_name': display_name,
                        'element_name': elem.tag,
                        'nickname': elem.get('NickName', ''),
                        'name': elem.get('Name', ''),
                        'guid': instance_guid
                    }

    def _process_grasshopper_object_chunk(self, object_chunk, object_index):
        """Process a single Grasshopper Object chunk to extract component information."""

        # Extract the component type GUID and Name from the Object chunk itself
        object_items = object_chunk.find('items')
        type_guid = None
        component_type_name = None

        if object_items is not None:
            for item in object_items.findall('item'):
                if item.get('name') == 'GUID' and item.text:
                    type_guid = item.text.strip()
                elif item.get('name') == 'Name' and item.text:
                    component_type_name = item.text.strip()

        # Find the Container chunk which contains the actual instance data
        container_chunk = object_chunk.find('.//chunk[@name="Container"]')
        if container_chunk is not None:
            self._process_container_chunk(container_chunk, type_guid, component_type_name, object_index)

    def _process_container_chunk(self, container_chunk, type_guid, component_type_name, object_index):
        """Process the Container chunk to extract component details."""
        # Look for InstanceGuid in the container items
        items = container_chunk.find('items')
        if items is None:
            return

        instance_guid = None
        name = None
        nickname = None
        source_count = 0
        user_text = None

        for item in items.findall('item'):
            item_name = item.get('name')
            if item_name == 'InstanceGuid' and item.text:
                instance_guid = item.text.strip()
            elif item_name == 'Name' and item.text:
                name = item.text.strip()
            elif item_name == 'NickName' and item.text:
                nickname = item.text.strip()
            elif item_name == 'SourceCount' and item.text:
                try:
                    source_count = int(item.text.strip())
                except ValueError:
                    source_count = 0
            elif item_name == 'UserText' and item.text:
                user_text = item.text.strip()

        if instance_guid:
            # Apply panel filtering logic
            if self._should_include_component(component_type_name, source_count, user_text):
                # Create display name
                display_name = nickname or name or component_type_name or f"Component_{instance_guid[:8]}"

                self.components[instance_guid] = {
                    'display_name': display_name,
                    'element_name': component_type_name or 'Unknown',
                    'nickname': nickname or '',
                    'name': name or '',
                    'guid': instance_guid,
                    'type_guid': type_guid,
                    'source_count': source_count,
                    'user_text': user_text or ''
                }

    def _should_include_component(self, component_type_name: str, source_count: int, user_text: str) -> bool:
        """
        Determine if a component should be included in the flow diagram analysis.

        Panel filtering rules:
        - Include panels if they are disconnected (SourceCount = 0) or part of a group
        - Ignore panels if they are connected to other nodes (SourceCount > 0)
        - Always include non-panel components
        """
        if component_type_name != 'Panel':
            return True  # Always include non-panel components

        # For panels: include only if disconnected (SourceCount = 0)
        # Connected panels are just displaying computed results
        if source_count == 0:
            # Include standalone panels (they contain documentation/notes)
            return True
        else:
            # Exclude connected panels (they're just displaying computed results)
            return False

    def _extract_connections(self, root):
        """Extract connections between components by analyzing GUID references in the archive format."""
        guid_pattern = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)

        # Look for DefinitionObjects chunk
        definition_objects = root.find('.//chunk[@name="DefinitionObjects"]')
        if definition_objects is not None:
            # Find all Object chunks
            obj_chunks = definition_objects.findall('.//chunk[@name="Object"]')

            for obj_chunk in obj_chunks:
                self._extract_connections_from_grasshopper_chunk(obj_chunk, guid_pattern)

        # Also scan the entire document for any connection patterns
        self._scan_document_for_connections(root, guid_pattern)

    def _extract_connections_from_grasshopper_chunk(self, object_chunk, guid_pattern):
        """Extract connections from a single Grasshopper Object chunk."""
        # Find the component's instance GUID from the Container chunk
        component_guid = None
        container_chunk = object_chunk.find('.//chunk[@name="Container"]')
        if container_chunk is not None:
            items = container_chunk.find('items')
            if items is not None:
                for item in items.findall('item'):
                    if item.get('name') == 'InstanceGuid' and item.text:
                        component_guid = item.text.strip()
                        break

        if not component_guid or component_guid not in self.components:
            return

        # Look for GUID references throughout the entire chunk
        self._find_guid_references_in_element(object_chunk, component_guid, guid_pattern)

    def _scan_document_for_connections(self, root, guid_pattern):
        """Scan the entire document for connection patterns."""
        # Look for any elements that might contain connection information
        for elem in root.iter():
            # Skip if this element has its own InstanceGuid (it's a component, not a connection)
            if elem.get('InstanceGuid'):
                continue

            # Look for GUID references in text and attributes
            self._find_connection_patterns(elem, guid_pattern)

    def _find_guid_references_in_element(self, elem, component_guid: str, guid_pattern):
        """Find GUID references that represent connections in an element tree."""
        # Check element text
        if elem.text and elem.text.strip():
            referenced_guids = guid_pattern.findall(elem.text)
            for ref_guid in referenced_guids:
                if ref_guid in self.components and ref_guid != component_guid:
                    self._add_connection_by_context(elem, component_guid, ref_guid)

        # Check attributes
        for attr_name, attr_value in elem.attrib.items():
            if attr_value and len(attr_value) >= 36:  # GUID length or longer
                referenced_guids = guid_pattern.findall(attr_value)
                for ref_guid in referenced_guids:
                    if ref_guid in self.components and ref_guid != component_guid:
                        self._add_connection_by_context(elem, component_guid, ref_guid, attr_name)

        # Check child elements recursively
        for child in elem:
            self._find_guid_references_in_element(child, component_guid, guid_pattern)

    def _find_connection_patterns(self, elem, guid_pattern):
        """Find connection patterns in elements without a specific component context."""
        # Look for elements that might represent connections
        if elem.text and elem.text.strip():
            referenced_guids = guid_pattern.findall(elem.text)
            if len(referenced_guids) >= 2:
                # Multiple GUIDs in same element might represent connections
                for i, source_guid in enumerate(referenced_guids[:-1]):
                    for target_guid in referenced_guids[i+1:]:
                        if (source_guid in self.components and
                            target_guid in self.components and
                            source_guid != target_guid):
                            # Assume first GUID is source, second is target
                            self._add_connection(source_guid, target_guid)

    def _add_connection_by_context(self, elem, component_guid: str, referenced_guid: str, attr_name: str = ''):
        """Add connection based on element context (input/output/source/target)."""
        context = (elem.tag + ' ' + attr_name).lower()

        # Determine connection direction based on context
        if any(keyword in context for keyword in ['input', 'source', 'from']):
            # referenced_guid -> component_guid (input connection)
            self.connections[referenced_guid].append(component_guid)
            self.reverse_connections[component_guid].append(referenced_guid)
        elif any(keyword in context for keyword in ['output', 'target', 'to', 'recipient']):
            # component_guid -> referenced_guid (output connection)
            self.connections[component_guid].append(referenced_guid)
            self.reverse_connections[referenced_guid].append(component_guid)
        else:
            # Default: assume it's an input reference
            self.connections[referenced_guid].append(component_guid)
            self.reverse_connections[component_guid].append(referenced_guid)

    def _add_connection(self, source_guid: str, target_guid: str):
        """Add a direct connection between two components."""
        if target_guid not in self.connections[source_guid]:
            self.connections[source_guid].append(target_guid)
        if source_guid not in self.reverse_connections[target_guid]:
            self.reverse_connections[target_guid].append(source_guid)

    def generate_flow_diagram(self) -> str:
        """Generate the main flow diagram output."""
        if not self.components:
            return "No components found in the XML file."

        output = []

        # Header
        output.append("# Flow Diagram Analysis")
        output.append("")
        output.append(f"**File:** {os.path.basename(self.xml_file_path)}")
        output.append(f"**Components:** {len(self.components)}")
        output.append(f"**Connections:** {sum(len(targets) for targets in self.connections.values())}")
        output.append("")

        # Main workflow paths
        main_paths = self._identify_main_workflow_paths()
        if main_paths:
            output.append("## Main Workflow Paths")
            output.append("")
            for i, path in enumerate(main_paths, 1):
                output.append(f"### Path {i}")
                if len(path) > 1:
                    path_str = " ---> ".join(self.components[guid]['display_name'] for guid in path)
                    output.append("```")
                    output.append(path_str)
                    output.append("```")
                else:
                    output.append(f"Single component: {self.components[path[0]]['display_name']}")
                output.append("")

        # Branching points
        branching_points = self._identify_branching_points()
        if branching_points:
            output.append("## Branching Points")
            output.append("")
            output.append("Components that split data flow into multiple paths:")
            output.append("")
            for source_guid, target_guids in branching_points.items():
                source_name = self.components[source_guid]['display_name']
                output.append(f"**{source_name}** branches to {len(target_guids)} components:")
                for target_guid in target_guids:
                    target_name = self.components[target_guid]['display_name']
                    output.append("```")
                    output.append(f"{source_name} ---> {target_name}")
                    output.append("```")
                output.append("")

        # Parallel processing
        parallel_groups = self._identify_parallel_processing()
        if parallel_groups:
            output.append("## Parallel Processing")
            output.append("")
            output.append("Groups of components processing the same inputs in parallel:")
            output.append("")
            for i, group in enumerate(parallel_groups, 1):
                output.append(f"### Parallel Group {i}")
                group_names = [self.components[guid]['display_name'] for guid in group]
                for j, name in enumerate(group_names):
                    if j == 0:
                        output.append("```")
                        output.append(f"Input ---> {name}")
                    else:
                        output.append(f"      ---> {name}")
                output.append("```")
                output.append("")

        # Merge points
        merge_points = self._identify_merge_points()
        if merge_points:
            output.append("## Merge Points")
            output.append("")
            output.append("Components that combine data from multiple sources:")
            output.append("")
            for target_guid, source_guids in merge_points.items():
                if len(source_guids) > 1:
                    target_name = self.components[target_guid]['display_name']
                    output.append(f"**{target_name}** receives from {len(source_guids)} components:")
                    for source_guid in source_guids:
                        source_name = self.components[source_guid]['display_name']
                        output.append("```")
                        output.append(f"{source_name} ---> {target_name}")
                        output.append("```")
                    output.append("")

        # Documentation panels (standalone panels with meaningful UserText)
        documentation_panels = self._find_documentation_panels()
        if documentation_panels:
            output.append("## Documentation Notes")
            output.append("")
            output.append("Standalone panels containing workflow documentation:")
            output.append("")
            for guid, user_text in documentation_panels.items():
                panel_name = self.components[guid]['display_name']
                output.append(f"**{panel_name}:** {user_text}")
            output.append("")

        # Summary
        output.append("## Flow Summary")
        output.append("")
        start_nodes = self._find_start_nodes()
        end_nodes = self._find_end_nodes()

        output.append(f"- **Start points:** {len(start_nodes)} components")
        for guid in start_nodes[:5]:  # Show first 5
            output.append(f"  - {self.components[guid]['display_name']}")

        output.append(f"- **End points:** {len(end_nodes)} components")
        for guid in end_nodes[:5]:  # Show first 5
            output.append(f"  - {self.components[guid]['display_name']}")

        output.append(f"- **Branching points:** {len(branching_points)}")
        output.append(f"- **Merge points:** {len(merge_points)}")
        output.append(f"- **Parallel groups:** {len(parallel_groups)}")
        output.append(f"- **Documentation panels:** {len(documentation_panels)}")

        return "\n".join(output)

    def _identify_main_workflow_paths(self) -> List[List[str]]:
        """Identify the main workflow paths from start to end nodes."""
        start_nodes = self._find_start_nodes()
        end_nodes = set(self._find_end_nodes())

        if not start_nodes:
            return []

        all_paths = []
        for start_node in start_nodes:
            paths = self._trace_paths_from_start(start_node, end_nodes, max_paths=3)
            all_paths.extend(paths)

        # Sort by path length and return the most significant ones
        all_paths.sort(key=len, reverse=True)
        return all_paths[:10]  # Return top 10 paths

    def _trace_paths_from_start(self, start_guid: str, end_nodes: Set[str], max_paths: int = 3) -> List[List[str]]:
        """Trace paths from a start node using breadth-first search."""
        paths = []
        queue = deque([(start_guid, [start_guid])])
        visited_paths = set()

        while queue and len(paths) < max_paths:
            current_guid, path = queue.popleft()

            # Convert path to tuple for hashing
            path_tuple = tuple(path)
            if path_tuple in visited_paths:
                continue
            visited_paths.add(path_tuple)

            # If we've reached an end node or have no more connections
            if current_guid in end_nodes or not self.connections[current_guid]:
                if len(path) > 1:  # Only include multi-component paths
                    paths.append(path)
                continue

            # Continue exploring
            for next_guid in self.connections[current_guid]:
                if next_guid not in path:  # Avoid cycles
                    new_path = path + [next_guid]
                    if len(new_path) <= 10:  # Limit path length
                        queue.append((next_guid, new_path))

        return paths

    def _find_start_nodes(self) -> List[str]:
        """Find nodes that likely represent workflow starting points."""
        # Nodes with no inputs are potential start points
        start_candidates = [guid for guid in self.components if not self.reverse_connections[guid]]

        # If no nodes without inputs, find nodes with minimal inputs
        if not start_candidates:
            min_inputs = min(len(self.reverse_connections[guid]) for guid in self.components)
            start_candidates = [guid for guid in self.components
                             if len(self.reverse_connections[guid]) == min_inputs]

        return start_candidates

    def _find_end_nodes(self) -> List[str]:
        """Find nodes that likely represent workflow endpoints."""
        # Nodes with no outputs are potential end points
        end_candidates = [guid for guid in self.components if not self.connections[guid]]

        # If no nodes without outputs, find nodes with minimal outputs
        if not end_candidates:
            min_outputs = min(len(self.connections[guid]) for guid in self.components)
            end_candidates = [guid for guid in self.components
                            if len(self.connections[guid]) == min_outputs]

        return end_candidates

    def _identify_branching_points(self) -> Dict[str, List[str]]:
        """Identify components that branch data flow into multiple paths."""
        return {guid: targets for guid, targets in self.connections.items() if len(targets) > 1}

    def _identify_merge_points(self) -> Dict[str, List[str]]:
        """Identify components that merge data from multiple sources."""
        return {guid: sources for guid, sources in self.reverse_connections.items() if len(sources) > 1}

    def _identify_parallel_processing(self) -> List[List[str]]:
        """Identify groups of components that process the same inputs in parallel."""
        # Group components by their input sources
        input_groups = defaultdict(list)

        for guid in self.components:
            inputs = tuple(sorted(self.reverse_connections[guid]))
            if inputs:  # Only consider components with inputs
                input_groups[inputs].append(guid)

        # Return groups with more than one component (parallel processing)
        parallel_groups = []
        for inputs, components in input_groups.items():
            if len(components) > 1:
                parallel_groups.append(components)

        return parallel_groups

    def _find_documentation_panels(self) -> Dict[str, str]:
        """Find standalone panels that contain meaningful documentation text."""
        documentation_panels = {}

        for guid, component in self.components.items():
            if (component['element_name'] == 'Panel' and
                component.get('source_count', 0) == 0 and  # Standalone panel
                component.get('user_text', '') and         # Has text content
                component.get('user_text', '') not in ['', 'Double click to edit panel content…']):  # Meaningful content
                documentation_panels[guid] = component['user_text']

        return documentation_panels


def main():
    """Main entry point for the flow diagram generator sub-agent."""
    if len(sys.argv) != 2:
        print("Usage: python flow_diagram_generator.py <xml_file_path>")
        print("")
        print("This sub-agent generates text-based flow diagrams from Grasshopper XML files.")
        print("It identifies main workflow paths, branching points, and parallel processing.")
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

    # Create and run the generator
    generator = FlowDiagramGenerator(xml_file_path)

    if not generator.analyze_xml():
        print("Error: Failed to analyze XML file")
        sys.exit(1)

    # Generate and output the flow diagram
    flow_diagram = generator.generate_flow_diagram()
    print(flow_diagram)


if __name__ == "__main__":
    main()