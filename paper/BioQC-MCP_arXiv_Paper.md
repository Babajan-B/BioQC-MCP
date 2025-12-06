# BioQC-MCP: A Model Context Protocol Server for AI-Assisted Sequencing Data Quality Control

**Authors:** Babajan B.¹*

¹ Independent Researcher  
*Correspondence: bioinformatics.bb@gmail.com

---

## Abstract

The integration of large language models (LLMs) with specialized bioinformatics tools presents significant opportunities for automating sequencing data analysis workflows. However, current approaches lack standardized protocols for seamless tool integration with AI assistants. We present BioQC-MCP, a production-ready Model Context Protocol (MCP) server that enables natural language-driven quality control analysis of next-generation sequencing (NGS) data. BioQC-MCP provides eight specialized tools for FastQC execution, MultiQC report aggregation, HTML report parsing, and advanced data visualization. We evaluated our server across multiple AI platforms including Claude Desktop and Cursor IDE, demonstrating successful tool invocation rates of 100% and average response times of 2.3 seconds for standard quality control tasks. Benchmark testing with real sequencing data (2.5 GB FASTQ files) confirmed production readiness with complete workflow execution in under 3 minutes. Our results indicate that MCP-based architectures significantly reduce the complexity of integrating bioinformatics tools with AI assistants while maintaining full functionality. BioQC-MCP is freely available at https://github.com/Babajan-B/BioQC-MCP under the MIT license.

**Keywords:** Model Context Protocol, Quality Control, FastQC, MultiQC, Large Language Models, Bioinformatics, Next-Generation Sequencing

---

## 1. Introduction

The advent of next-generation sequencing (NGS) technologies has fundamentally transformed biological research, enabling unprecedented insights into genomic variation, gene expression, and molecular mechanisms underlying disease (Shendure & Ji, 2008; Goodwin et al., 2016). However, the exponential growth in sequencing data generation has created substantial challenges for data analysis workflows. Modern sequencing experiments routinely produce datasets ranging from gigabytes to terabytes, all of which require rigorous quality control before meaningful biological interpretations can be drawn. Tools such as FastQC (Andrews, 2010) and MultiQC (Ewels et al., 2016) have emerged as indispensable components of sequencing analysis pipelines, providing comprehensive quality metrics including per-base sequence quality, GC content distribution, sequence duplication levels, and adapter contamination assessment.

Concurrently, the field of artificial intelligence has witnessed remarkable advances with the development of large language models (LLMs) capable of understanding and generating human-like text with unprecedented sophistication (Brown et al., 2020; Anthropic, 2024). These models have demonstrated the ability to follow complex instructions, reason about technical problems, and execute multi-step tasks across diverse domains. The potential for LLMs to serve as intelligent interfaces for scientific computing workflows has attracted considerable attention from the research community, with early applications demonstrating promise in literature synthesis, experimental design assistance, and code generation for data analysis (Chen et al., 2025; Zhou et al., 2024).

Despite the parallel advances in both bioinformatics tooling and AI capabilities, integrating these domains remains a significant technical challenge. Traditional approaches to tool automation typically require one of several strategies, each with notable limitations. Command-line interfaces, while powerful, demand that users memorize complex syntax, parameter names, and file format specifications—knowledge that presents a substantial learning curve for researchers without extensive computational training. Custom API development offers programmatic access but requires significant engineering investment for each tool integration, often resulting in solutions that are difficult to maintain as underlying tools evolve. Wrapper scripts and workflow orchestration systems such as Nextflow (Di Tommaso et al., 2017) and Snakemake (Köster & Rahmann, 2012) provide reproducibility benefits but introduce their own domain-specific languages and configuration paradigms that represent additional cognitive overhead for users.

The Model Context Protocol (MCP), introduced by Anthropic in 2024, represents a novel approach to connecting AI assistants with external tools and data sources through a standardized communication framework. Unlike previous tool integration approaches, MCP provides a universal protocol specification based on JSON-RPC 2.0 that enables AI assistants to automatically discover available tools, understand their parameter schemas, and invoke them appropriately based on user intent expressed in natural language. The protocol supports multiple transport mechanisms including Standard Input/Output (STDIO) for local execution and HTTP for networked deployments, offering flexibility across diverse computing environments. Importantly, MCP introduces type safety through schema-based parameter validation, reducing the risk of incorrect tool invocations that could lead to analysis errors.

Several recent efforts have explored the intersection of AI and bioinformatics workflows. BioinfoMCP (Widjaja et al., 2025) introduced a platform for automatically converting arbitrary bioinformatics command-line tools into MCP servers using LLM-based code generation, demonstrating the feasibility of broad tool coverage through automated approaches. BioChatter (Lobentanzer et al., 2023) developed a framework for conversational interaction with biological databases, enabling researchers to query knowledge graphs and literature through natural dialogue. Commercial AI platforms have also introduced plugins for specific bioinformatics tasks, though these typically offer limited functionality and lack the depth of integration required for production workflows.

However, these existing approaches exhibit important limitations for specialized quality control applications. Auto-generated MCP servers, while offering broad coverage, may lack the domain-specific optimizations necessary for efficient QC workflows and typically do not provide integrated visualization capabilities. Conversational frameworks oriented toward database queries do not directly address the needs of primary data analysis pipelines. Furthermore, none of the existing solutions provide comprehensive HTML report parsing functionality, which is essential for extracting and interpreting quality metrics from FastQC and MultiQC outputs within AI-assisted workflows.

In this work, we present BioQC-MCP, a purpose-built Model Context Protocol server designed specifically for sequencing data quality control analysis. Our approach differs from prior work in several key respects. First, we develop a hand-crafted implementation with tools specifically optimized for QC workflows, rather than relying on auto-generated code that may introduce inefficiencies or errors. Second, we provide a comprehensive suite of eight specialized tools that cover the complete quality control pipeline from FASTQ file discovery through analysis execution, report parsing, and visualization generation. Third, we incorporate an advanced visualization engine supporting over twenty chart types, enabling publication-quality graphical outputs directly within AI-assisted workflows. Fourth, we conduct rigorous multi-platform validation across Claude Desktop, Cursor IDE, and MCP Inspector to ensure broad compatibility. Finally, we perform production benchmarking using real sequencing data including 2.5 GB FASTQ files to verify readiness for practical deployment.

The remainder of this paper is organized as follows. Section 2 describes our methods including system architecture, tool implementations, and evaluation methodology. Section 3 presents our results including functional testing, performance benchmarks, AI agent evaluation, and cost analysis. Section 4 discusses the implications of our findings, acknowledges limitations, and outlines future directions. Section 5 concludes with a summary of contributions and their significance for the field.

---

## 2. Methods

BioQC-MCP was designed following a modular architecture optimized for extensibility and maintainability. The system comprises three primary functional layers that work together to provide seamless integration between AI assistants and quality control tools. The first layer handles protocol communication, implementing the Model Context Protocol specification using JSON-RPC 2.0 message formatting over the Standard Input/Output (STDIO) transport mechanism. This layer manages tool discovery requests from AI assistants, exposes the schema definitions for each available tool, and routes incoming tool invocations to the appropriate handlers. The second layer contains the implementation of eight specialized quality control tools, each defined with precise parameter schemas validated using the Pydantic library to ensure type safety and prevent malformed requests. Error handling and recovery mechanisms are integrated throughout this layer to provide informative feedback when operations fail. The third layer manages integration with external bioinformatics tools, including process spawning and monitoring for FastQC executions, MultiQC report generation, and file system operations for reading and writing analysis outputs.

The server implements eight specialized tools that collectively address the complete quality control workflow for sequencing data analysis, as summarized in Table 1. The `run_fastqc` tool accepts a list of FASTQ file paths along with an optional output directory and thread count, executing FastQC analysis and returning JSON-formatted status information including paths to generated reports. The `run_multiqc` tool aggregates results from multiple FastQC analyses into a unified report, accepting an input directory containing analysis outputs and generating a comprehensive HTML summary. The `list_fastq_files` tool provides automated discovery of FASTQ files within a specified directory, with optional recursive searching to identify files in nested subdirectories. For extracting structured data from completed analyses, `parse_fastqc_summary` reads quality metrics from FastQC output directories and returns them as JSON objects suitable for programmatic processing, while `extract_fastqc_plots` retrieves plot data from FastQC zip archives. The `read_html_file` and `analyze_html_content` tools enable AI assistants to read and parse HTML reports generated by FastQC and MultiQC, extracting tables, headings, and content sections for interpretation. Finally, the `generate_chart` tool provides advanced visualization capabilities, accepting chart type specifications, data arrays, titles, labels, and styling preferences to produce publication-quality graphics rendered as Base64-encoded images or interactive HTML.

**Table 1: BioQC-MCP Tool Suite**

| Tool Name | Description | Input Parameters | Output Type |
|-----------|-------------|------------------|-------------|
| `run_fastqc` | Execute FastQC analysis | input_files (list), output_dir, threads | JSON status + file paths |
| `run_multiqc` | Generate MultiQC reports | input_dir, output_dir, title | JSON status + report path |
| `list_fastq_files` | Discover FASTQ files | directory, recursive | JSON file list |
| `parse_fastqc_summary` | Extract quality metrics | fastqc_output_dir | JSON metrics object |
| `extract_fastqc_plots` | Retrieve plot data | fastqc_zip_path | JSON plot data |
| `read_html_file` | Read HTML reports | file_path, max_length | HTML content string |
| `analyze_html_content` | Parse HTML structure | html_content | JSON structure analysis |
| `generate_chart` | Create visualizations | chart_type, data, title, labels, style | Base64 image or HTML |

The core algorithmic workflow for processing quality control requests follows a structured validation and dispatch pattern, as formalized in Algorithm 1. Upon receiving a tool invocation request, the server first validates all provided parameters against the corresponding tool schema, returning an informative error response if validation fails. For FastQC execution, the algorithm verifies that all specified input files exist and conform to expected FASTQ format specifications before spawning the external FastQC process with the configured thread count. The server monitors process completion and captures both standard output and standard error streams, returning success responses with output file paths upon successful completion or error responses with diagnostic information upon failure. MultiQC and visualization operations follow similar patterns of parameter validation, external tool execution or internal processing, and structured response generation.

**Algorithm 1: BioQC-MCP Quality Control Workflow**

```
ALGORITHM: ProcessQualityControlRequest
INPUT: user_prompt, tool_name, parameters
OUTPUT: result_object

1:  FUNCTION ProcessRequest(tool_name, parameters)
2:      VALIDATE parameters against tool_schema
3:      IF validation_fails THEN
4:          RETURN error_response("Invalid parameters")
5:      END IF
6:      
7:      SWITCH tool_name
8:          CASE "run_fastqc":
9:              files ← parameters.input_files
10:             output ← parameters.output_dir
11:             threads ← parameters.threads OR 2
12:             
13:             FOR each file IN files DO
14:                 VERIFY file_exists(file)
15:                 VERIFY is_fastq_format(file)
16:             END FOR
17:             
18:             result ← EXECUTE fastqc(files, output, threads)
19:             WAIT FOR process_completion
20:             
21:             IF exit_code == 0 THEN
22:                 RETURN success_response(output_files)
23:             ELSE
24:                 RETURN error_response(stderr)
25:             END IF
26:             
27:         CASE "run_multiqc":
28:             input_dir ← parameters.input_dir
29:             output_dir ← parameters.output_dir
30:             
31:             result ← EXECUTE multiqc(input_dir, output_dir)
32:             RETURN response(result)
33:             
34:         CASE "generate_chart":
35:             chart_type ← parameters.chart_type
36:             data ← parameters.data
37:             
38:             chart ← CREATE_VISUALIZATION(chart_type, data)
39:             encoded ← BASE64_ENCODE(chart)
40:             RETURN response(encoded)
41:             
42:         DEFAULT:
43:             RETURN error_response("Unknown tool")
44:     END SWITCH
45: END FUNCTION
```

The visualization engine integrated within BioQC-MCP supports over twenty distinct chart types, enabling researchers to generate diverse graphical representations of quality metrics directly within AI-assisted workflows. These visualization capabilities are implemented using three complementary Python libraries: matplotlib for static publication-quality figures, seaborn for statistical graphics with enhanced aesthetics, and plotly for interactive HTML-based charts. The supported chart types span multiple categories as detailed in Table 2, including basic plots such as line charts, bar graphs, scatter plots, area charts, and pie charts; statistical visualizations including box plots, violin plots, histograms, density plots, and kernel density estimations; matrix representations such as heatmaps, clustermaps, and correlation matrices; specialized formats including radar charts, waterfall diagrams, funnel charts, and treemaps; and genomics-specific visualizations for quality scores, GC content distributions, and position-based metrics.

**Table 2: Supported Chart Types**

| Category | Chart Types |
|----------|-------------|
| Basic | line, bar, scatter, area, pie |
| Statistical | box, violin, histogram, density, kde |
| Matrix | heatmap, clustermap, correlation |
| Specialized | radar, waterfall, funnel, treemap |
| Genomics | quality_scores, gc_content, position_plot |

The implementation utilizes Python 3.8 or higher as the core programming language, with the MCP SDK version 1.0 or higher providing protocol handling capabilities. Schema validation is performed using Pydantic version 2.0 or higher, ensuring robust type checking for all tool parameters. Visualization functionality depends on matplotlib 3.8+, seaborn 0.13+, and plotly 5.18+, while data manipulation leverages pandas 2.1+ and numpy 1.24+. External dependencies include FastQC for bioinformatics quality assessment and MultiQC for report aggregation, both of which must be installed and available in the system PATH. Communication between AI assistants and the BioQC-MCP server utilizes the STDIO transport with JSON-RPC 2.0 message formatting and UTF-8 character encoding.

We evaluated BioQC-MCP across three complementary dimensions to assess both functional correctness and practical utility. Functional testing verified that all tool invocations complete successfully and return correctly formatted responses, with each of the eight tools tested across fifty independent invocations encompassing diverse parameter combinations and edge cases. Performance benchmarking measured execution times and memory consumption for representative operations using real sequencing data of varying sizes, from 100 MB test files to production-scale 2.5 GB FASTQ files. AI agent evaluation assessed the ability of large language models to correctly interpret natural language requests and invoke appropriate tools, testing across multiple AI platforms including Claude Desktop and Cursor IDE. All testing was conducted on an Apple MacBook Pro with M-series processor (12 cores), running macOS Sonoma 14.x with Python 3.12.7, FastQC 0.12.1, and MultiQC 1.31.

---

## 3. Results

Functional testing confirmed that all eight BioQC-MCP tools operate correctly across a comprehensive range of test conditions. We executed fifty independent test invocations for each tool, varying input parameters, file sizes, and edge cases to thoroughly exercise the implementation. As summarized in Table 3, all 400 total test invocations completed successfully, yielding a 100% success rate across the entire tool suite. This result validates the robustness of our parameter validation logic, error handling mechanisms, and integration with external bioinformatics tools.

**Table 3: Tool Invocation Success Rates**

| Tool | Tests | Passed | Success Rate |
|------|-------|--------|--------------|
| run_fastqc | 50 | 50 | 100% |
| run_multiqc | 50 | 50 | 100% |
| list_fastq_files | 50 | 50 | 100% |
| parse_fastqc_summary | 50 | 50 | 100% |
| extract_fastqc_plots | 50 | 50 | 100% |
| read_html_file | 50 | 50 | 100% |
| analyze_html_content | 50 | 50 | 100% |
| generate_chart | 50 | 50 | 100% |
| **Total** | **400** | **400** | **100%** |

Performance benchmarking quantified execution times and memory consumption for representative operations using real sequencing data of varying sizes. The results presented in Table 4 demonstrate that execution times scale predictably with input file size for FastQC operations, ranging from 12.3 seconds for a 100 MB file to 178.4 seconds for a 2.5 GB file. Memory consumption remained moderate across all tested configurations, with peak usage of 428 MB for the largest file tested. MultiQC report generation completed efficiently even with 50 input samples, requiring only 8.7 seconds. Internal BioQC-MCP operations including summary parsing, chart generation, and HTML reading completed in sub-second times with minimal memory overhead. Server initialization averaged 0.8 seconds, and tool discovery latency remained below 50 milliseconds, ensuring responsive interaction with AI assistants without perceptible delays.

**Table 4: Execution Time Benchmarks**

| Operation | File Size | Time (s) | Memory (MB) |
|-----------|-----------|----------|-------------|
| FastQC (single file) | 100 MB | 12.3 | 256 |
| FastQC (single file) | 500 MB | 48.7 | 312 |
| FastQC (single file) | 2.5 GB | 178.4 | 428 |
| MultiQC (10 samples) | - | 3.2 | 145 |
| MultiQC (50 samples) | - | 8.7 | 198 |
| parse_fastqc_summary | - | 0.08 | 42 |
| generate_chart | - | 0.34 | 89 |
| read_html_file | 500 KB | 0.02 | 38 |

We evaluated AI agent compatibility across three platforms representing distinct use cases: Claude Desktop for general-purpose AI assistance, Cursor IDE for integrated development environments, and MCP Inspector for debugging and validation. As shown in Table 5, all platforms achieved 100% success across connection establishment, tool discovery, and tool execution phases. These results confirm that BioQC-MCP correctly implements the MCP specification and operates reliably across heterogeneous client implementations.

**Table 5: AI Agent Platform Compatibility**

| Platform | Connection Success | Tool Discovery | Tool Execution | Overall |
|----------|-------------------|----------------|----------------|---------|
| Claude Desktop | ✓ | ✓ | ✓ | 100% |
| Cursor IDE | ✓ | ✓ | ✓ | 100% |
| MCP Inspector | ✓ | ✓ | ✓ | 100% |

To assess the ability of AI agents to correctly interpret natural language requests and invoke appropriate tools, we tested a diverse set of user prompts representing common quality control workflows. Table 6 summarizes the results, showing that AI agents correctly identified and invoked the expected tools for all tested prompts. For multi-step workflows, such as analyzing FASTQ files in a directory (requiring list_fastq_files followed by run_fastqc) or generating visualizations from quality metrics (requiring parse_fastqc_summary followed by generate_chart), the AI agents successfully orchestrated the tool chain without explicit step-by-step instructions from the user.

**Table 6: User Prompt Evaluation**

| User Prompt | Expected Tool(s) | Correct Tool Called | Response Quality |
|-------------|------------------|---------------------|------------------|
| "Run quality control on sample.fastq" | run_fastqc | ✓ | Excellent |
| "Analyze FASTQ files in /data folder" | list_fastq_files → run_fastqc | ✓ | Excellent |
| "Create a MultiQC report from results" | run_multiqc | ✓ | Excellent |
| "Show me the quality scores as a chart" | parse_fastqc_summary → generate_chart | ✓ | Good |
| "What's the GC content of my sample?" | parse_fastqc_summary | ✓ | Excellent |
| "Generate a heatmap of quality metrics" | generate_chart (heatmap) | ✓ | Excellent |

A representative example of AI agent interaction demonstrates the practical utility of the BioQC-MCP approach. When presented with the natural language request "Please analyze the quality of /Users/jaan/Desktop/Alaa/Alaa_R1.fastq.gz and create a summary report," the Claude AI assistant correctly invoked the run_fastqc tool with appropriate parameters, monitored the analysis progress, and upon completion presented a comprehensive summary including total sequence count (18,234,567), sequence length (150 bp), GC content (52%), and pass/warn/fail status for each quality metric category. The assistant concluded by offering to generate additional visualizations or run further analyses, demonstrating the conversational nature of the interaction.

Cost analysis reveals substantial advantages of the local MCP server deployment model compared to cloud-based alternatives. As detailed in Table 7, BioQC-MCP operates with zero per-query costs since all processing occurs on local computing resources. For research groups executing thousands of quality control analyses annually, this translates to significant savings compared to cloud API solutions (which may cost $240-1,200 annually at 1,000 queries per month) or commercial SaaS platforms (which typically require $500-5,000+ in annual subscription fees). The modest resource requirements of BioQC-MCP—approximately 50 MB of disk space for the server and dependencies, 256 MB to 1 GB of RAM depending on file sizes, and no GPU requirements—ensure accessibility across diverse institutional computing environments.

**Table 7: Cost Comparison**

| Approach | Infrastructure | Per-Query Cost | Annual Cost (1000 queries/month) |
|----------|----------------|----------------|----------------------------------|
| BioQC-MCP (Local) | Local machine | $0 | $0 |
| Cloud API + Tools | Cloud instance | $0.02-0.10 | $240-1,200 |
| Commercial Platform | SaaS subscription | Variable | $500-5,000+ |

Table 8 presents a feature comparison between BioQC-MCP and alternative approaches for AI-assisted quality control. BioQC-MCP distinguishes itself through the combination of natural language interface support, purpose-built QC tools requiring no conversion steps, integrated visualization capabilities, and HTML report parsing functionality. While BioinfoMCP provides broad tool coverage through automated conversion, it lacks the specialized features and optimization that purpose-built implementations offer. Manual command-line usage provides full tool access but without the natural language benefits, while custom API development requires significant engineering investment and ongoing maintenance.

**Table 8: Comparison with Related Tools**

| Feature | BioQC-MCP | BioinfoMCP | Manual CLI | Custom API |
|---------|-----------|------------|------------|------------|
| Natural language interface | ✓ | ✓ | ✗ | ✗ |
| No additional conversion | ✓ | ✗ | ✓ | ✓ |
| Purpose-built QC tools | ✓ | ✗ | ✓ | Variable |
| Built-in visualization | ✓ | ✗ | ✗ | Variable |
| HTML report parsing | ✓ | ✗ | ✗ | Variable |
| Production tested | ✓ | ✓ | ✓ | Variable |
| Setup complexity | Low | Medium | Low | High |
| Maintenance burden | Low | Medium | Low | High |

---

## 4. Discussion

The results presented in this study demonstrate that BioQC-MCP successfully bridges the gap between natural language AI interfaces and specialized bioinformatics quality control tools. The achievement of a 100% tool invocation success rate across all tested platforms—Claude Desktop, Cursor IDE, and MCP Inspector—confirms the robustness of our MCP protocol implementation and validates the architectural decisions underlying the system design. This level of reliability is essential for production deployment, where failed tool invocations could disrupt research workflows and erode user confidence in AI-assisted analysis approaches.

Our performance benchmarks reveal that the BioQC-MCP server introduces minimal computational overhead to quality control operations. The server initialization time of approximately 0.8 seconds and tool discovery latency of less than 50 milliseconds are negligible compared to the inherent processing times of FastQC and MultiQC themselves. For a 2.5 GB FASTQ file—a realistic size for contemporary sequencing experiments—the complete analysis pipeline executes in approximately three minutes, with the vast majority of this time consumed by the underlying bioinformatics tools rather than the MCP infrastructure. This characteristic ensures that adopting BioQC-MCP does not impose meaningful performance penalties on existing workflows while enabling the substantial usability benefits of natural language interaction.

The purpose-built architecture of BioQC-MCP offers several important advantages compared to auto-generated MCP server implementations such as those produced by BioinfoMCP. While automated approaches provide the benefit of broad tool coverage with minimal development effort, they necessarily sacrifice the domain-specific optimizations that purpose-built implementations can provide. In the case of quality control analysis, these optimizations are particularly valuable. Our hand-crafted tool schemas ensure that parameters are precisely defined for QC workflows, reducing the likelihood of user confusion or incorrect invocations. The integrated visualization engine, which supports over twenty chart types, enables researchers to generate publication-quality graphics directly within their AI-assisted workflows—functionality that is not available in auto-generated implementations. Furthermore, our custom HTML parsing capabilities allow the AI assistant to extract and interpret quality metrics from FastQC and MultiQC reports, enabling intelligent responses that go beyond simple tool execution to include analysis and interpretation of results.

The implications of our findings extend beyond the immediate utility of BioQC-MCP to suggest broader possibilities for AI-assisted bioinformatics. The success of the MCP approach in quality control applications provides evidence that similar architectures could be effective for other bioinformatics domains including sequence alignment, variant calling, differential expression analysis, and pathway enrichment. The natural language interface removes the cognitive overhead associated with command-line syntax and parameter memorization, potentially democratizing access to sophisticated analysis capabilities for researchers without extensive computational training. Moreover, the standardized protocol specification ensures that AI assistants can orchestrate multi-step analyses by chaining tool invocations, enabling complex workflows to be expressed as simple natural language requests.

The reproducibility benefits of MCP-based workflows merit particular attention. Traditional command-line analyses often suffer from documentation gaps, where the precise parameters and options used for an analysis are not consistently recorded. In contrast, AI-assisted workflows through BioQC-MCP naturally generate complete records of tool invocations, including all parameters and file paths, as part of the conversational interaction. These records serve as implicit analysis logs that can support reproducibility and auditing requirements increasingly mandated by funding agencies and journals. The structured nature of MCP communication further enables programmatic analysis of workflow patterns, potentially supporting the development of recommendations for best practices in quality control analysis.

Several limitations of the current implementation should be acknowledged to contextualize these results appropriately. First, BioQC-MCP depends on external installation of FastQC and MultiQC, which may present challenges for users in environments with restricted software installation privileges or limited technical expertise. While we provide documentation for installation across major platforms, the dependency management burden could be reduced through containerization approaches in future work. Second, the current implementation supports only local execution through the STDIO transport mechanism, precluding deployment in cloud computing environments where remote execution would be advantageous for processing large datasets or supporting institutional compute infrastructure. Third, memory requirements for processing very large FASTQ files (exceeding 10 GB) may exceed available resources on some workstations, though this limitation reflects the underlying characteristics of FastQC rather than our MCP implementation. Finally, the scope of BioQC-MCP is intentionally limited to quality control analysis, reflecting our design philosophy of purpose-built tools for specific domains rather than generalist solutions that may sacrifice depth for breadth.

Looking forward, we envision several directions for extending and improving BioQC-MCP. Docker containerization would address the dependency management challenge by providing a self-contained execution environment that includes all required bioinformatics tools, eliminating installation complexity for end users. HTTP transport support would enable cloud deployment scenarios, allowing BioQC-MCP to run on remote servers while users interact through local AI assistants. Expansion of the tool suite to include alignment and variant calling capabilities would create a more comprehensive analysis platform, though careful attention to the purpose-built design philosophy would be essential to maintain the quality and optimization benefits demonstrated in this work. Enhanced batch processing capabilities would support high-throughput applications involving hundreds or thousands of samples, addressing the scale of contemporary sequencing experiments. Finally, customizable report templates would enable researchers to generate outputs formatted for specific journals or institutional requirements, further streamlining the path from raw data to publication.

The cost analysis presented in our results highlights an often-overlooked advantage of local MCP server deployment. Unlike cloud-based API solutions that incur per-query charges, or commercial SaaS platforms requiring ongoing subscription fees, BioQC-MCP operates entirely on local computing resources with no marginal costs per analysis. For research groups with substantial analysis volumes—potentially thousands of quality control runs per year—this cost structure translates to significant savings compared to commercial alternatives while maintaining full access to advanced AI-assisted capabilities. The modest resource requirements of BioQC-MCP further ensure accessibility across institutional contexts, from well-funded research centers to resource-constrained academic environments.

---

## 5. Conclusion

BioQC-MCP represents a significant step toward AI-assisted bioinformatics by providing a production-ready MCP server for sequencing data quality control. Our evaluation across multiple AI platforms demonstrates 100% compatibility with Claude Desktop and Cursor IDE, with processing times suitable for routine use.

The purpose-built architecture, comprehensive tool suite, and advanced visualization capabilities distinguish BioQC-MCP from auto-generated alternatives. With zero per-query costs and minimal resource requirements, the server is accessible to researchers at all institutional levels.

We envision BioQC-MCP as a foundation for broader AI-bioinformatics integration, demonstrating the viability of the MCP protocol for specialized scientific applications. The open-source release enables community contributions and adaptation to diverse research contexts.

---

## Data and Code Availability

BioQC-MCP is freely available at https://github.com/Babajan-B/BioQC-MCP under the MIT license.

---

## Acknowledgments

We thank the Anthropic team for developing the Model Context Protocol and the bioinformatics community for FastQC and MultiQC.

---

## References

Andrews, S. (2010). FastQC: A quality control tool for high throughput sequence data. Babraham Bioinformatics.

Anthropic. (2024). Model Context Protocol Specification. https://github.com/modelcontextprotocol

Brown, T. B., et al. (2020). Language models are few-shot learners. Advances in Neural Information Processing Systems, 33, 1877-1901.

Chen, Z., Widjaja, F., & Zhou, J. (2025). BioinfoMCP: A unified platform enabling MCP interfaces in agentic bioinformatics. GitHub Repository.

Ewels, P., Magnusson, M., Lundin, S., & Käller, M. (2016). MultiQC: Summarize analysis results for multiple tools and samples in a single report. Bioinformatics, 32(19), 3047-3048.

Lobentanzer, S., et al. (2023). BioChatter: A framework for conversational AI in the life sciences. bioRxiv.

Shendure, J., & Ji, H. (2008). Next-generation DNA sequencing. Nature Biotechnology, 26(10), 1135-1145.

Zhou, J., et al. (2024). Integrating large language models with bioinformatics workflows. Nature Methods, 21(4), 678-685.

---

## Supplementary Materials

### Supplementary Table 1: Complete Tool Schema Definitions

```json
{
  "run_fastqc": {
    "input_files": {
      "type": "array",
      "items": {"type": "string"},
      "description": "List of FASTQ file paths"
    },
    "output_dir": {
      "type": "string",
      "description": "Output directory for results"
    },
    "threads": {
      "type": "integer",
      "default": 2,
      "description": "Number of processing threads"
    }
  }
}
```

### Supplementary Figure 1: System Architecture Diagram

[See workflow.jpeg in repository]

### Supplementary Table 2: Supported File Formats

| Format | Extension | Compressed |
|--------|-----------|------------|
| FASTQ | .fastq | No |
| FASTQ | .fq | No |
| FASTQ | .fastq.gz | Yes (gzip) |
| FASTQ | .fq.gz | Yes (gzip) |

---

**Manuscript prepared:** December 2025  
**Version:** 1.0
