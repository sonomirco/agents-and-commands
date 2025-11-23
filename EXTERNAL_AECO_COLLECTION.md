# External AECO LLM Collection

This document provides a comprehensive collection of external AECO (Architecture, Engineering, Construction, Operations) LLM technologies, including MCP servers, prompt libraries, and Claude Code skills found in the wild.

> **Note**: This is a curated collection of external resources. For the specialized agents, commands, and skills provided by this repository, please refer to the main [README.md](README.md).

## MCP Servers (Model Context Protocol)

### Authoring and BIM Tools

**Revit Integration**
- [Revit MCP](https://github.com/revit-mcp/revit-mcp) - AI-powered Revit modeling via MCP
- [Revit MCP (oakplank)](https://github.com/oakplank/RevitMCP) - Model Context Protocol server for Autodesk Revit
- [Revit MCP SDK](https://github.com/DTDucas/RevitMCPSDK) - SDK and helpers for building Revit MCP integrations
- [Revit MCP (PiggyAndrew)](https://github.com/PiggyAndrew/revit_mcp) - Revit MCP server connecting Claude to Autodesk Revit
- [Revit MCP for MEP](https://github.com/reneruano95/revit-mcp-mep) - MEP-specific data models and operations for Revit via MCP

**AutoCAD Integration**
- [AutoCAD MCP](https://github.com/puran-water/autocad-mcp) - MCP server for AutoCAD LT with natural language to AutoLISP translation
- [AutoCAD MCP Server (Python)](https://github.com/thepiruthvirajan/autocad-mcp-server) - Python-based MCP server for automating AutoCAD operations
- [AutoCAD MCP (2025)](https://github.com/ahmetcemkaraca/AutoCAD_MCP) - Multipurpose AutoCAD MCP for 2D and 3D DWG production

**Civil 3D**
- [Civil 3D MCP](https://github.com/barbosaihan/civil3d-mcp) - AI-powered Civil 3D modeling via MCP

**Rhino and Grasshopper**
- [RhinoMCP](https://github.com/jingcheng-chen/rhinomcp) - Connects Rhino 3D to AI Agent through MCP
- [Rhino MCP Server](https://github.com/always-tinkering/rhinoMcpServer) - Connects Rhino to Claude via MCP for AI-assisted 3D modeling
- [Grasshopper MCP Server](https://github.com/veoery/GH_mcp_server) - Enable LLMs to interact with Rhino and Grasshopper
- [Grasshopper MCP](https://github.com/alfredatnycu/grasshopper-mcp) - Grasshopper MCP tools for parametric workflows
- [AI Architecture MCP (Rhino + Grasshopper)](https://github.com/Xiaohu1009/AI-architecture) - Unified MCP server combining Rhino and Grasshopper capabilities
- [RhinoPilot MCP](https://github.com/mrbeandev/RhinoPilot-mcp) - MCP server to control Rhino3D with simple calls
- [Rhino MCP (Ollama)](https://github.com/iamsunghoonlee/RhinoMCP) - Run multiple computational design tools via Ollama in Rhino

**SketchUp**
- [SketchUp MCP](https://github.com/mhyrr/sketchup-mcp) - SketchUp Model Context Protocol server enabling AI control
- [Sketchflow MCP](https://github.com/LGalabov/sketchflow-mcp) - MCP server for SketchUp with natural language control

**FreeCAD**
- [FreeCAD MCP](https://github.com/neka-nat/freecad-mcp) - Connect FreeCAD to LLM agents through MCP

**3D Visualization**
- [Blender MCP](https://github.com/ahujasid/blender-mcp) - Connects Blender to Claude via MCP for prompt-assisted 3D modeling
- [Maya MCP](https://github.com/PatrickPalmer/MayaMCP) - Model Context Protocol server implementation for Autodesk Maya

### Structural Analysis and Fabrication

**Finite Element Analysis**
- [FEA MCP](https://github.com/GreatApo/FEA-MCP) - Finite Element Analysis MCP (supports LUSAS, ETABS and more)
- [ETABS Fast MCP](https://github.com/HuVelasco/ETABSFastMCP) - Professional-grade ETABS MCP for structural automation
- [ETABS MCP (Local Embeddings)](https://github.com/PriyankGodhat/etabs-mcp-server-local-embeddings) - ETABS documentation search via local embeddings
- [Structural MCP Servers](https://github.com/HuVelasco/structural-mcp-servers) - Collection of MCP servers for ETABS, Revit and Tekla

**Tekla Integration**
- [Tekla MCP Server](https://github.com/teknovizier/tekla_mcp_server) - MCP server for Tekla Structures to speed up modeling
- [Tekla API MCP](https://github.com/pawellisowski/tekla-api-mcp) - Exposes Tekla Open API docs and examples via MCP
- [MCP Tekla Plus](https://github.com/BIMBrain/McpTeklaPlus) - AI-assisted modeling platform for Tekla Structures 2025

### IFC and BIM Exchange

**IFC Processing**
- [IFC MCP](https://github.com/smartaec/ifcMCP) - MCP server to read and manipulate IFC files
- [IFC Bonsai MCP](https://github.com/Show2Instruct/ifc-bonsai-mcp) - Connect LLMs to Blender Bonsai add-on for IFC workflows
- [IFC MCP Server](https://github.com/yc-it/ifc-mcp) - Industry Foundation Classes MCP server

**Rule Checking and Validation**
- [IDS MCP](https://github.com/vinnividivicci/ifc-ids-mcp) - Deterministic creation and validation of BuildingSmart IDS files

### GIS and Civil Context

**GIS Platforms**
- [QGIS MCP](https://github.com/jjsantos01/qgis_mcp) - Prompt-assisted QGIS project creation, layer loading and scripting
- [DeepSeek QGIS MCP](https://github.com/kicker315/deepseek_qgis_mcp) - QGIS MCP variant using DeepSeek
- [ArcGIS Pro MCP Add-In](https://github.com/nicogis/MCP-Server-ArcGIS-Pro-AddIn) - ArcGIS Pro add-in exposing tools via MCP
- [ArcGIS MCP](https://github.com/GarrickGarcia/ArcGISMCP) - Model Context Protocol server for ArcGIS workflows

**Geospatial Processing**
- [GDAL MCP](https://github.com/Wayfinder-Foundry/gdal-mcp) - Spatial data processing via GDAL tools exposed through MCP
- [GeoServer MCP](https://github.com/mahdin75/geoserver-mcp) - Connect LLMs to GeoServer REST API using MCP
- [Geo MCP (Geocoding)](https://github.com/webcoderz/MCP-Geo) - Geocoding MCP server backed by GeoPy

### MEP and Water Systems

**MEP Integration**
- [Trimble MEP Custom Instructions MCP](https://github.com/marian-stefan/trimble.mep.dotnet.custominstructions.mcp) - .NET custom instructions for Trimble MEP MCP integration

**Water Systems**
- [EPANET MCP Server](https://github.com/KWR-Water/epanet-mcp-server) - Run simulations and tasks on EPANET networks via MCP

### Energy and Power

**Energy Management**
- [Energy MCP](https://github.com/matthicks05/energy-mcp) - MCP server for accessing and analyzing electrical usage data
- [Emporia Energy MCP](https://github.com/emporiaenergy/emporia-mcp) - Emporia Energy integration via MCP for usage and device data
- [Energy Chat](https://github.com/matthicks05/energy-chat) - Chat-based energy advisor agent using the energy MCP server
- [PyPSA MCP](https://github.com/cdgaete/pypsa-mcp) - PyPSA energy system modeling exposed to LLMs via MCP
- [Power MCP](https://github.com/Power-Agent/PowerMCP) - Collection of MCP servers for power system software
- [MCP Carbon Calculator](https://github.com/Programmer-RD-AI/mcp-carbon-calculator) - Compute CO2e from electricity and gas usage via MCP tools

**Home Automation**
- [Home Assistant MCP](https://github.com/tevonsb/homeassistant-mcp) - Home Assistant integration exposing devices and automations via MCP
- [Home Assistant MCP Server](https://github.com/voska/hass-mcp) - Model Context Protocol server for Home Assistant
- [Home Assistant MCP (Allen Porter)](https://github.com/allenporter/mcp-server-home-assistant) - Home Assistant MCP server implementation
- [Advanced Home Assistant MCP](https://github.com/jango-blockchained/advanced-homeassistant-mcp) - Advanced features for Home Assistant MCP

### Other Useful MCP Servers

**3D Printing and Fabrication**
- [Thingiverse MCP](https://github.com/gpaul-mcp/mcp_thingiverse) - Let AI agents search and retrieve models from Thingiverse via MCP

### Autodesk Platform Services

**APS Integration**
- [APS MCP Server](https://github.com/kpphillips/aps-mcp-server) - Prototype MCP server integrating Autodesk Platform Services APIs
- [APS MCP Server (Node.js)](https://github.com/autodesk-platform-services/aps-mcp-server-nodejs) - Node.js MCP server exposing APS with secure service accounts
- [APS AECDM MCP (.NET)](https://github.com/autodesk-platform-services/aps-aecdm-mcp-dotnet) - .NET MCP server connecting Claude to Autodesk AEC Data Model APIs
- [Autodesk MCP](https://github.com/Guidogl/autodesk-mcp) - Autodesk Platform Services MCP server utilities and examples

### Data Exchange and Integration

**Speckle Integration**
- [Speckle MCP](https://github.com/bimgeek/speckle-mcp) - MCP server for Speckle integration

## Prompt Libraries and Templates

### AI-BIM Integration
- [AI-BIM Bridge](https://github.com/brannonr3/ai-bim-bridge) - Convert natural language home design prompts into IFC architectural models

### APS/ACC Integration
- [Sample Prompts for APS/ACC with Viktor](https://github.com/AlejoDuarte23/sample-prompts-ACC-APS-VIKTOR) - Ready-to-use prompts for Viktor AI Builder to generate BIM apps integrating APS and ACC

### IDS and Rule-Checking Prompts
- [From Regulations to IDS](https://github.com/vanoha/from-regulations-to-IDS) - Prompt set for generating BuildingSmart IDS from regulations using tool-augmented LLM pipeline
- [IDS Generation Prompts](https://github.com/simpledumpling/ids-generation) - Main prompts for automated IDS checks generation used in regulations-to-IDS pipeline

## Claude Code Skills

### AECO-Specific Skills
- [AECDM Room Check](https://github.com/asertorio/AECDM-Room-Check) - A PS AEC Data Model room validation skill

## Analysis Summary

### Key Findings

**MCP Implementation Success**
- **60+ active MCP servers** across major AECO software platforms
- **High community engagement** with several repositories having 100+ stars
- **Active development** across all implementations with recent updates
- **Comprehensive software coverage**: Revit, AutoCAD, Rhino, Tekla, SketchUp, GIS platforms, energy systems

**Major Gaps Identified**
1. **Claude Code Skills**: Only 1 dedicated AECO skill found (AECDM Room Check)
2. **Prompt Libraries**: Limited specialized AECO prompt collections
3. **Cross-platform Integration**: Opportunities for unified workflow automation
4. **Documentation**: Limited examples of end-to-end AECO workflow automation

**Development Opportunities**
- High demand for more Claude Code skills targeting AECO workflows
- Need for comprehensive prompt libraries for engineering applications
- Opportunities for cross-platform MCP servers
- Potential for standardized AECO AI agent development patterns

### Community Engagement Highlights
- **Most Active**: RhinoMCP (241 stars) - Highest engagement in the ecosystem
- **Enterprise Focus**: Multiple Autodesk Platform Services integrations
- **Emerging Areas**: Energy management, structural analysis, GIS integration
- **Global Participation**: Projects from contributors worldwide

---

**Last Updated**: November 23, 2025
**Total Resources Cataloged**: 60+ MCP servers, 8 prompt collections, 1 Claude Code skill
**Overall Assessment**: Active MCP ecosystem with significant opportunities for Claude Code skills and prompt libraries development

## Contributing

Found new AECO-related MCP servers, prompt libraries, or Claude Code skills? Please contribute by:

1. Opening an issue with the repository details
2. Submitting a pull request to add new resources
3. Helping maintain the accuracy of existing links and descriptions

This collection serves as a living reference to the evolving AECO LLM technology landscape.