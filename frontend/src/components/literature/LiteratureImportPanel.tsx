import { useRef, useState, type ChangeEvent } from 'react'

import { api } from '@/api/client'
import type { UploadedDocument } from '@/types'

interface Props {
  experimentId: string
  documents: UploadedDocument[]
  onUpdated: () => void
}

export function LiteratureImportPanel({ experimentId, documents, onUpdated }: Props) {
  const fileRef = useRef<HTMLInputElement>(null)
  const imageRef = useRef<HTMLInputElement>(null)
  const [isHandout, setIsHandout] = useState(false)
  const [url, setUrl] = useState('')
  const [uploading, setUploading] = useState(false)
  const [parsing, setParsing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const uploadFile = async (file: File) => {
    setUploading(true)
    setError(null)
    try {
      await api.uploadDocument(experimentId, file, isHandout)
      onUpdated()
    } catch (err) {
      setError(err instanceof Error ? err.message : '上传失败')
    } finally {
      setUploading(false)
    }
  }

  const handleFile = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await uploadFile(file)
    if (fileRef.current) fileRef.current.value = ''
  }

  const handleImage = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await uploadFile(file)
    if (imageRef.current) imageRef.current.value = ''
  }

  const handleUrl = async () => {
    if (!url.trim()) {
      setError('请输入网址')
      return
    }
    setUploading(true)
    setError(null)
    try {
      await api.addDocumentUrl(experimentId, url.trim(), isHandout)
      setUrl('')
      onUpdated()
    } catch (err) {
      setError(err instanceof Error ? err.message : '添加失败')
    } finally {
      setUploading(false)
    }
  }

  const handleParse = async () => {
    if (documents.length === 0) {
      setError('请先上传文献或添加网址')
      return
    }
    if (
      !confirm(
        'AI 将解析文献并生成实验步骤，已有步骤将被替换。是否继续？'
      )
    ) {
      return
    }
    setParsing(true)
    setError(null)
    try {
      await api.parseLiterature(experimentId)
      onUpdated()
    } catch (err) {
      setError(err instanceof Error ? err.message : '解析失败')
    } finally {
      setParsing(false)
    }
  }

  const handleDeleteDoc = async (docId: number) => {
    if (!confirm('确定删除该文献？')) return
    try {
      await api.deleteDocument(experimentId, docId)
      onUpdated()
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败')
    }
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <h4 className="text-sm font-semibold text-slate-800">文献导入</h4>
      <p className="mt-1 text-xs text-slate-500">
        支持 PDF、DOCX、实验相关图片（讲义/板书/仪器说明）与部分公开网址。勾选「教师讲义」时优先以讲义为准。
      </p>
      <p className="mt-1 text-xs text-slate-500">
        图片将自动 OCR 识别文字，并在「AI 解析」时由 DeepSeek 整理后生成步骤（请尽量拍摄清晰、平整的画面）。
      </p>
      <p className="mt-1 text-xs text-amber-700">
        知网 / 万方等数据库链接无法直接抓取（需登录），请下载 PDF 后上传。
      </p>

      <label className="mt-3 flex items-center gap-2 text-sm text-slate-700">
        <input
          type="checkbox"
          checked={isHandout}
          onChange={(e) => setIsHandout(e.target.checked)}
          className="rounded border-slate-300 text-brand-600"
        />
        标记为教师讲义（优先）
      </label>

      <div className="mt-3 flex flex-wrap gap-2">
        <input
          ref={fileRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => void handleFile(e)}
        />
        <input
          ref={imageRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          className="hidden"
          onChange={(e) => void handleImage(e)}
        />
        <button
          type="button"
          disabled={uploading}
          onClick={() => fileRef.current?.click()}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm hover:bg-slate-100 disabled:opacity-50"
        >
          {uploading ? '上传中…' : '上传 PDF / DOCX'}
        </button>
        <button
          type="button"
          disabled={uploading}
          onClick={() => imageRef.current?.click()}
          className="rounded-lg border border-brand-200 bg-brand-50 px-3 py-2 text-sm text-brand-800 hover:bg-brand-100 disabled:opacity-50"
        >
          {uploading ? '上传中…' : '上传图片分析'}
        </button>
      </div>

      <div className="mt-3 flex flex-col gap-2 sm:flex-row">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://..."
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          type="button"
          disabled={uploading}
          onClick={() => void handleUrl()}
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm hover:bg-slate-100 disabled:opacity-50"
        >
          添加网址
        </button>
      </div>

      {documents.length > 0 && (
        <ul className="mt-4 space-y-2">
          {documents.map((doc) => (
            <li
              key={doc.id}
              className="flex items-center justify-between rounded-lg bg-white px-3 py-2 text-sm"
            >
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-medium text-slate-800">{doc.filename}</span>
                  {doc.is_handout && (
                    <span className="rounded bg-amber-100 px-1.5 py-0.5 text-xs text-amber-800">
                      讲义
                    </span>
                  )}
                  <span className="text-xs text-slate-400 uppercase">{doc.doc_type}</span>
                  {doc.doc_type === 'image' && (
                    <span
                      className={`text-xs ${doc.has_text ? 'text-green-700' : 'text-amber-700'}`}
                    >
                      {doc.has_text ? '已识别文字' : '待解析识别'}
                    </span>
                  )}
                </div>
                {doc.preview_url && (
                  <a
                    href={doc.preview_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-2 inline-block"
                  >
                    <img
                      src={doc.preview_url}
                      alt={doc.filename}
                      className="max-h-24 rounded border border-slate-200 object-contain"
                    />
                  </a>
                )}
                {doc.source_url && (
                  <p className="truncate text-xs text-slate-500">{doc.source_url}</p>
                )}
              </div>
              <button
                type="button"
                onClick={() => void handleDeleteDoc(doc.id)}
                className="ml-2 shrink-0 text-xs text-red-600 hover:underline"
              >
                删除
              </button>
            </li>
          ))}
        </ul>
      )}

      <button
        type="button"
        disabled={parsing || documents.length === 0}
        onClick={() => void handleParse()}
        className="mt-4 w-full rounded-lg bg-brand-600 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto sm:px-6"
      >
        {parsing ? 'AI 解析中（含图片识别），请稍候…' : 'AI 解析并生成步骤'}
      </button>

      {error && (
        <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      )}
    </div>
  )
}
