import { Divider, Modal } from 'antd';
import Editor from '@monaco-editor/react';

function SchemaModal({ open, schemaText, onClose }) {
  return (
    <Modal
      title="ScriptDocument JSON Schema"
      open={open}
      onCancel={onClose}
      footer={null}
      width={900}
    >
      <Divider />
      <div className="schema-view">
        <Editor
          height="460px"
          language="json"
          value={schemaText}
          theme="vs-dark"
          options={{
            readOnly: true,
            minimap: { enabled: false },
            wordWrap: 'on',
            scrollBeyondLastLine: false,
          }}
        />
      </div>
    </Modal>
  );
}

export default SchemaModal;
