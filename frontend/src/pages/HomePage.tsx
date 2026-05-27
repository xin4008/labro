import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <div className="mx-auto max-w-2xl rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h3 className="text-xl font-semibold text-slate-900">开始你的实验记录</h3>
      <p className="mt-2 text-sm leading-relaxed text-slate-600">
        支持<strong>化学</strong>、<strong>物理</strong>与<strong>生物</strong>实验：文献/图片
        AI 解析、分步数据记录、Word 报告导出。新建实验时选择学科即可匹配对应模板与 AI 提示。
      </p>
      <ul className="mt-6 space-y-2 text-sm text-slate-700">
        <li className="flex gap-2">
          <span className="text-brand-600">1.</span>
          创建实验项目并选择数据记录模板
        </li>
        <li className="flex gap-2">
          <span className="text-brand-600">2.</span>
          上传 PDF / DOCX 或网址，AI 解析生成步骤
        </li>
        <li className="flex gap-2">
          <span className="text-brand-600">3.</span>
          实验进行中逐步录入数据，自动保存
        </li>
        <li className="flex gap-2">
          <span className="text-brand-600">4.</span>
          顶栏「导出 Word」生成实验报告
        </li>
      </ul>
      <Link
        to="/experiments/new"
        className="mt-8 inline-flex rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
      >
        新建实验
      </Link>
    </div>
  )
}
