import Editor from '@monaco-editor/react';
import { Dialog, DialogContentAnimated, DialogHeader, DialogTitle } from './ui/dialog';

function SchemaModal({ open, schemaText, onClose }) {
  return (
    <Dialog open={open} onOpenChange={(nextOpen) => !nextOpen && onClose()}>
      <DialogContentAnimated open={open}>
        <DialogHeader>
          <DialogTitle>ScriptDocument JSON Schema</DialogTitle>
        </DialogHeader>
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
      </DialogContentAnimated>
    </Dialog>
  );
}

export default SchemaModal;
