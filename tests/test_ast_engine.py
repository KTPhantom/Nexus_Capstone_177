"""
Unit tests for TSX AST parser and noise filter.
"""

from nexus.parser.ast_engine import TSXComponentParser
from nexus.parser.noise_filter import clean_semantic_tsx, strip_tailwind_classes


SAMPLE_TSX = """
import React, { useState, useEffect } from 'react';

/**
 * @name SampleWidget
 * @domain student
 * @description A test widget for unit testing AST parsing.
 * @capability test-cap, widget-tool
 * @author Test Author
 */

export interface SampleWidgetProps {
  title: string;
  count?: number;
  onAction?: (val: string) => void;
}

export const SampleWidget: React.FC<SampleWidgetProps> = ({ title, count = 0, onAction }) => {
  const [active, setActive] = useState<boolean>(true);
  const [text, setText] = useState<string>('hello');

  useEffect(() => {
    console.log("Mounted");
  }, []);

  return (
    <div className="p-4 bg-slate-900 text-white rounded-xl shadow-lg border border-slate-700">
      <h1 className="text-xl font-bold">{title}</h1>
      <button
        onClick={() => setActive(!active)}
        className={`px-3 py-1 ${active ? 'bg-indigo-600' : 'bg-slate-700'}`}
      >
        Toggle
      </button>
      <svg className="w-4 h-4"><path d="M0 0h24v24H0z"/></svg>
    </div>
  );
};

export default SampleWidget;
"""


def test_noise_filtering():
    cleaned = clean_semantic_tsx(SAMPLE_TSX)
    assert "bg-slate-900" not in cleaned
    assert "rounded-xl" not in cleaned
    assert "shadow-lg" not in cleaned
    assert "<path d=" not in cleaned
    assert "<Icon />" in cleaned
    assert "onClick=" in cleaned
    assert "Toggle" in cleaned


def test_ast_parsing_metadata():
    parser = TSXComponentParser()
    meta = parser.parse_source(SAMPLE_TSX, relative_path="registry/student/SampleWidget.tsx")

    assert meta.name == "SampleWidget"
    assert meta.domain == "student"
    assert "test-cap" in meta.capabilities
    assert "widget-tool" in meta.capabilities
    assert meta.description == "A test widget for unit testing AST parsing."
    assert meta.author == "Test Author"

    # Props verification
    assert meta.props_interface_name == "SampleWidgetProps"
    assert len(meta.props) == 3
    prop_names = {p.name: p for p in meta.props}
    assert "title" in prop_names
    assert not prop_names["title"].is_optional
    assert "count" in prop_names
    assert prop_names["count"].is_optional

    # Hooks verification
    hook_types = [h.hook_type for h in meta.hooks]
    assert "useState" in hook_types
    assert "useEffect" in hook_types

    # Hash verification
    assert len(meta.raw_code_sha256) == 64
    assert len(meta.semantic_sha256) == 64


def test_semantic_hash_invariance():
    """
    Modifying only Tailwind CSS classes should change raw_code_sha256
    but preserve semantic_sha256!
    """
    parser = TSXComponentParser()
    meta1 = parser.parse_source(SAMPLE_TSX, relative_path="registry/student/SampleWidget.tsx")

    # Change only className styling
    modified_code = SAMPLE_TSX.replace("bg-slate-900", "bg-emerald-950")
    meta2 = parser.parse_source(modified_code, relative_path="registry/student/SampleWidget.tsx")

    assert meta1.raw_code_sha256 != meta2.raw_code_sha256
    assert meta1.semantic_sha256 == meta2.semantic_sha256


def test_ast_parsing_type_alias_and_nested_props():
    """
    Test extraction of props when defined via 'type FooProps = { ... }'
    and when props contain nested curly braces.
    """
    source = """
    import React from 'react';
    /**
     * @name AdvancedComponent
     * @domain student
     * @description Component testing type alias and nested props.
     */
    export type AdvancedComponentProps = {
        title: string;
        config: { timeout: number; debug: boolean };
        onComplete?: (result: { status: string; code: number }) => void;
        retries?: number;
    };
    export const AdvancedComponent: React.FC<AdvancedComponentProps> = () => null;
    """
    parser = TSXComponentParser()
    meta = parser.parse_source(source, relative_path="registry/student/AdvancedComponent.tsx")

    assert meta.name == "AdvancedComponent"
    assert meta.props_interface_name == "AdvancedComponentProps"
    assert len(meta.props) == 4
    prop_names = {p.name: p for p in meta.props}
    assert "title" in prop_names
    assert "config" in prop_names
    assert "onComplete" in prop_names
    assert "retries" in prop_names
    assert prop_names["retries"].is_optional
    assert "{ timeout: number; debug: boolean }" in prop_names["config"].type_signature


def test_ast_parsing_generics_and_useref():
    """
    Test hook extraction with generic arguments like useState<Array<string>>
    and useRef hooks.
    """
    source = """
    import React, { useState, useRef } from 'react';
    export const HookWidget = () => {
        const [items, setItems] = useState<Array<string>>([]);
        const [record, setRecord] = useState<Record<string, number>>({});
        const inputRef = useRef<HTMLInputElement>(null);
        return <div>Test</div>;
    };
    """
    parser = TSXComponentParser()
    meta = parser.parse_source(source, relative_path="registry/student/HookWidget.tsx")

    assert meta.name == "HookWidget"
    hook_vars = {h.state_variable: h for h in meta.hooks}
    assert "items" in hook_vars
    assert hook_vars["items"].inferred_type == "Array<string>"
    assert "record" in hook_vars
    assert hook_vars["record"].inferred_type == "Record<string, number>"
    assert "inputRef" in hook_vars
    assert hook_vars["inputRef"].hook_type == "useRef"
