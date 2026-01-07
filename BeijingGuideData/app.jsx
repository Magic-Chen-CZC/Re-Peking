import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Database, 
  Table, 
  Image, 
  FlaskConical, 
  RefreshCcw, 
  Settings, 
  Search, 
  Bell, 
  User, 
  ChevronRight, 
  Upload, 
  Filter, 
  Plus, 
  Trash2, 
  Eye, 
  FileText, 
  MoreHorizontal,
  X,
  CheckCircle,
  AlertCircle,
  Clock,
  Download,
  Save,
  MessageSquare,
  Cpu,
  ArrowRight,
  GitCommit,
  Edit3,
  Activity,
  Server,
  Layers,
  FileWarning,
  HelpCircle,
  Zap,
  HardDrive,
  PieChart,
  Loader,
  BarChart3,
  List,
  AlertTriangle,
  FileQuestion,
  History,
  Sliders,
  BookOpen,
  Key,
  Shield,
  ChevronDown,
  ChevronRight as ChevronRightIcon,
  ToggleLeft,
  UserPlus,
  Lock,
  RefreshCw,
  Phone,
  Smartphone,
  ChevronLeft,
  LogIn,
  LogOut,
  UserCog,
  Power,
  Contact,
  Archive,
  Ban,
  RotateCcw,
  FileDiff,
  Wrench
} from 'lucide-react';

// --- Mock Data ---

const MOCK_PDF_FILES = [
  { id: 1, name: 'J7_2024_用户手册.pdf', type: 'pdf', model: 'J7', category: '保用', size: '5.2 MB', time: '2023-10-24 10:00', uploader: '张三', chunks: 128, status: 'ready' },
  { id: 2, name: '鹰途_发动机维修指引.docx', type: 'doc', model: '鹰途', category: '保养', size: '2.8 MB', time: '2023-10-24 11:30', uploader: '李四', chunks: 0, status: 'processing' },
  { id: 3, name: 'J7_电路维修手册_草稿.pdf', type: 'pdf', model: 'J7', category: '维修', size: '12.5 MB', time: '2023-10-26 09:15', uploader: '技术部', chunks: 0, status: 'pending_review', markdownContent: '# J7 电路维修手册 (草稿)\n\n## 1. 整车电源分配\n整车电源分为常电（BAT）、ACC电源和IG电源。\n\n- **BAT**: 直接连接蓄电池，不受钥匙控制。\n- **ACC**: 钥匙打到ACC档位接通。\n- **IG**: 钥匙打到ON档位接通。\n\n## 2. CAN 总线网络\n车辆配备3路CAN总线：\n1. 动力CAN (500kbps)\n2. 车身CAN (125kbps)\n3. 诊断CAN (500kbps)\n\n> 注意：维修时请务必断开蓄电池负极。' },
];

const MOCK_EXCEL_FILES = [
  { id: 101, name: '2024_全系故障码表.xlsx', type: 'excel', model: '全部', category: '故障', size: '1.2 MB', time: '2023-10-25 09:00', uploader: '王五', chunks: 1500, status: 'ready' },
  { id: 102, name: '鹰途_底盘参数规格.csv', type: 'excel', model: '鹰途', category: '功能', size: '0.5 MB', time: '2023-10-23 14:20', uploader: '赵六', chunks: 320, status: 'error', failureReason: 'Embedding 失败: 数据格式错误 (Invalid CSV Format)' },
];

const MOCK_IMAGE_FILES = [
  { id: 201, name: 'J7_仪表盘图标集.xlsx', type: 'image', model: 'J7', category: '故障', size: '45 KB', time: '2023-10-20 16:45', uploader: '设计部', chunks: 85, status: 'ready' },
  { id: 202, name: '鹰途_发动机舱实拍.csv', type: 'image', model: '鹰途', category: '保养', size: '12 KB', time: '2023-10-18 11:10', uploader: '李四', chunks: 0, status: 'pending_review', markdownContent: '## 图片描述\n- 图1: 发动机冷却液加注口，位于左侧。\n- 图2: 机油尺位置，黄色拉环。\n\n需要人工确认OCR识别的标签是否准确。' },
];

const MOCK_EXCEL_ROWS = [
  { id: '001', name: '气缸失火', code: 'P0300', desc: '检测到发动机随机/多缸失火', cause: '火花塞老化、点火线圈故障、喷油嘴堵塞', solution: '1.检查火花塞间隙; 2.更换点火线圈; 3.清洗油路。' },
  { id: '002', name: '氧传感器低电压', code: 'P0131', desc: '氧传感器电路电压过低（库1，传感器1）', cause: '传感器损坏、线路短路或断路、混合气过稀', solution: '检查传感器线路连接，必要时更换前氧传感器。' },
  { id: '003', name: '水温过高', code: 'P0217', desc: '发动机冷却液温度超出正常范围', cause: '节温器卡滞、冷却液不足、散热风扇故障', solution: '待发动机冷却后检查液位，检查节温器开度。' },
  { id: '004', name: '系统电压低', code: 'P0562', desc: '系统电压低于下限值', cause: '发电机故障、蓄电池亏电、接地不良', solution: '检查发电机皮带张紧度，测试蓄电池健康度。' },
  { id: '005', name: '燃油压力低', code: 'P0087', desc: '燃油轨/系统压力 - 甚至过低', cause: '高压油泵故障、燃油滤清器堵塞', solution: '更换燃油滤清器，检查高压泵数据流。' },
];

const MOCK_IMAGE_ITEMS = [
  { id: 1, name: '发动机故障灯', src: 'check_engine', color: 'yellow', desc: '黄色引擎轮廓图标', cause: '发动机电子控制系统检测到故障码', solution: '建议低速行驶至最近维修站进行诊断，避免剧烈驾驶。' },
  { id: 2, name: '机油压力报警', src: 'oil_pressure', color: 'red', desc: '红色油壶滴油图标', cause: '机油压力不足或机油量低于下限', solution: '危险！请立即停车熄火。检查机油尺液位，如不足请补充。如液位正常仍报警，请拖车维修。' },
  { id: 3, name: '水温报警灯', src: 'coolant_temp', color: 'red', desc: '红色温度计波浪图标', cause: '发动机冷却液温度过高', solution: '立即停车怠速散热，切勿直接熄火（防抱缸）。严禁立即打开水箱盖。' },
  { id: 4, name: 'ABS 故障灯', src: 'abs_warning', color: 'yellow', desc: '黄色圆圈内含ABS字样', cause: '防抱死刹车系统失效', solution: '常规刹车功能保留，但紧急制动无防抱死功能。建议谨慎驾驶并送修。' },
  { id: 5, name: '安全带未系', src: 'seatbelt', color: 'red', desc: '红色人形系带图标', cause: '驾驶员或乘客未系安全带', solution: '请系好安全带。' },
  { id: 6, name: '胎压异常', src: 'tire_pressure', color: 'yellow', desc: '黄色括号内感叹号', cause: '轮胎气压过低或过高', solution: '停车检查轮胎外观，使用胎压计测量并调整至标准值。' },
];

const MOCK_IMAGE_REVIEW_DATA = {
  name: '制动系统故障',
  color: 'red',
  desc: '红色圆圈内含感叹号图标',
  cause: '制动液液位过低或制动系统故障',
  solution: '立即停车检查制动液液位。如液位正常，可能是刹车片磨损严重。'
};

const MOCK_RLHF = [
  // 待处理
  { id: 1, userQ: '为什么我的车启动时有滋滋声？', aiAns: '可能是发动机皮带老化。', agentAns: '冷启动滋滋声通常与起动机或皮带有关，建议先检查...', diff: '85%', status: 'pending', date: '2023-10-26 14:20', reason: '答案不完整' },
  { id: 4, userQ: 'J7 2024款最大马力是多少？', aiAns: '560马力。', agentAns: '应该是620马力，请确认数据。', diff: '15%', status: 'pending', date: '2023-10-26 11:05', reason: '数据错误' },
  
  // 已入库
  { 
    id: 2, 
    userQ: 'P0300是什么故障？', 
    aiAns: '这是发动机失火代码。', 
    agentAns: 'P0300表示随机多缸失火，可能原因包括火花塞...', 
    diff: '40%', 
    status: 'processed', 
    date: '2023-10-25 16:40',
    originalDoc: '>> 来源：故障代码表_v1.xlsx\n行号：102\n内容：P0300 | 发动机一般故障 | 请检查发动机',
    modifiedDoc: '>> 来源：故障代码表_v1.xlsx\n行号：102\n内容：P0300 | 随机/多缸失火检测 | 1.检查火花塞 2.检查点火线圈'
  },
  { 
    id: 5, 
    userQ: '鹰途保养周期？', 
    aiAns: '5万公里。', 
    agentAns: '鹰途车型采用10万公里长换油技术。', 
    diff: '90%', 
    status: 'processed', 
    date: '2023-10-25 09:30',
    originalDoc: '>> 来源：鹰途_保养手册.pdf\n片段：建议每 50,000 公里更换一次机油。',
    modifiedDoc: '>> 来源：鹰途_保养手册.pdf\n片段：鹰途车型采用 100,000 公里长换油技术，建议每 10万公里更换一次机油。'
  },
  
  // 已忽略
  { id: 3, userQ: '如何煮咖啡？', aiAns: '对不起，我只回答汽车相关问题。', agentAns: '无', diff: '0%', status: 'ignored', reason: '无关问题', date: '2023-10-24 18:15' },
];

const MOCK_LOGS = [
  { id: 1, time: '2023-10-24 14:30', user: 'Admin', action: '配置修改', detail: '更新了 RAG 阈值 0.6 -> 0.65', status: 'success' },
  { id: 2, time: '2023-10-24 11:20', user: 'Knowledge Spec', action: '数据删除', detail: '删除了文档 X7_旧版手册.pdf', status: 'warning' },
  { id: 3, time: '2023-10-23 09:15', user: 'Admin', action: '用户管理', detail: '新增用户 guest_01', status: 'success' },
];

const MOCK_USERS = [
  { id: 1, name: 'Admin User', email: 'admin@company.com', role: 'Super Admin', status: 'Active' },
  { id: 2, name: 'Knowledge Spec', email: 'editor@company.com', role: 'Knowledge Specialist', status: 'Active' },
];

const MOCK_SKILLS = [
  { name: '保养excel处理', status: 'active' },
  { name: '保养pdf处理', status: 'active' },
  { name: '保用excel处理', status: 'active' },
  { name: '故障码excel处理', status: 'active' },
  { name: '故障灯图库处理', status: 'active' },
  { name: '用车功能pdf处理', status: 'active' },
  { name: '功能图库处理', status: 'active' },
  { name: '维修案例pdf处理', status: 'inactive' }, // Demo scrolling
  { name: '电路图识别处理', status: 'inactive' },
  { name: '语音故障识别', status: 'inactive' },
];

// --- Shared Components ---

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <div 
    onClick={onClick}
    className={`flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors ${
      active ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600' : 'text-slate-600 hover:bg-slate-50'
    }`}
  >
    <Icon size={20} />
    <span className="font-medium text-sm">{label}</span>
  </div>
);

const StatusBadge = ({ status }) => {
  if (status === 'ready') return <span className="flex items-center gap-1.5 text-xs font-medium text-green-600 bg-green-50 px-2.5 py-1 rounded-full"><span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>已就绪</span>;
  if (status === 'processing') return <span className="flex items-center gap-1.5 text-xs font-medium text-yellow-600 bg-yellow-50 px-2.5 py-1 rounded-full"><RefreshCcw size={10} className="animate-spin"/>处理中</span>;
  if (status === 'error') return <span className="flex items-center gap-1.5 text-xs font-medium text-red-600 bg-red-50 px-2.5 py-1 rounded-full"><AlertCircle size={10}/>失败</span>;
  if (status === 'pending_review') return <span className="flex items-center gap-1.5 text-xs font-medium text-purple-600 bg-purple-50 px-2.5 py-1 rounded-full"><FileText size={12}/>待审核</span>;
  
  if (status === 'processed') return <span className="flex items-center gap-1.5 text-xs font-medium text-green-600 bg-green-50 px-2.5 py-1 rounded-full"><CheckCircle size={12}/>已入库</span>;
  if (status === 'ignored') return <span className="flex items-center gap-1.5 text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full"><Ban size={12}/>已忽略</span>;
  if (status === 'pending') return <span className="flex items-center gap-1.5 text-xs font-medium text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full"><Clock size={12}/>待处理</span>;

  return null;
};

// --- Modals & Drawers ---

const LoginModal = ({ onClose, onLogin }) => {
  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-xl shadow-2xl w-[400px] p-8 animate-in zoom-in-95 duration-200 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600">
          <X size={20} />
        </button>
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-4 text-blue-600">
            <Lock size={32} />
          </div>
          <h3 className="text-xl font-bold text-slate-800">用户登录</h3>
          <p className="text-sm text-slate-500 mt-1">请输入账号密码以切换身份</p>
        </div>
        <div className="space-y-5">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">账号</label>
            <input type="text" placeholder="admin / user" className="w-full border border-slate-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1">密码</label>
            <input type="password" placeholder="••••••••" className="w-full border border-slate-300 rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
          </div>
        </div>
        <div className="mt-8 flex gap-3">
          <button onClick={onClose} className="flex-1 px-4 py-2.5 text-sm font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors">关闭</button>
          <button onClick={onLogin} className="flex-1 px-4 py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors flex items-center justify-center gap-2">
            <LogIn size={16}/> 登录
          </button>
        </div>
      </div>
    </div>
  );
};

const AddUserModal = ({ onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-xl shadow-xl w-[500px] p-6">
        <h3 className="text-lg font-bold text-slate-800 mb-6">新增用户</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
               <label className="block text-xs font-bold text-slate-500 mb-1">用户名</label>
               <input type="text" className="w-full border rounded p-2 text-sm" />
            </div>
            <div>
               <label className="block text-xs font-bold text-slate-500 mb-1">邮箱</label>
               <input type="email" className="w-full border rounded p-2 text-sm" />
            </div>
          </div>
          <div>
             <label className="block text-xs font-bold text-slate-500 mb-1">初始密码</label>
             <input type="text" defaultValue="123456" className="w-full border rounded p-2 text-sm bg-slate-50 text-slate-500" readOnly />
             <p className="text-xs text-slate-400 mt-1">默认密码为 123456</p>
          </div>
          <div>
             <label className="block text-xs font-bold text-slate-500 mb-1">角色权限</label>
             <select className="w-full border rounded p-2 text-sm">
               <option>知识专员</option>
               <option>只读访客</option>
               <option>超级管理员</option>
             </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-8">
          <button onClick={onClose} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded">取消</button>
          <button onClick={onClose} className="px-4 py-2 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded">确定新增</button>
        </div>
      </div>
    </div>
  );
};

const EditUserModal = ({ user, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-xl shadow-xl w-[500px] p-6">
        <h3 className="text-lg font-bold text-slate-800 mb-6">修改用户权限</h3>
        <div className="space-y-4">
          <div className="bg-slate-50 p-4 rounded border border-slate-100 mb-4">
            <p className="text-sm font-medium text-slate-800">{user.name}</p>
            <p className="text-xs text-slate-500">{user.email}</p>
          </div>
          <div>
             <label className="block text-xs font-bold text-slate-500 mb-1">当前角色</label>
             <select className="w-full border rounded p-2 text-sm" defaultValue={user.role}>
               <option>知识专员</option>
               <option>只读访客</option>
               <option>超级管理员</option>
             </select>
          </div>
        </div>
        <div className="flex justify-between items-center mt-8 pt-4 border-t">
          <button className="text-red-600 text-sm hover:text-red-800 flex items-center gap-1">
            <Trash2 size={16}/> 删除此用户
          </button>
          <div className="flex gap-3">
            <button onClick={onClose} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded">取消</button>
            <button onClick={onClose} className="px-4 py-2 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded">保存修改</button>
          </div>
        </div>
      </div>
    </div>
  );
};

const LogDetailModal = ({ log, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-xl shadow-xl w-[600px] p-6">
        <div className="flex justify-between items-center mb-4 border-b pb-4">
          <h3 className="text-lg font-bold text-slate-800">日志详情</h3>
          <button onClick={onClose}><X size={20} className="text-slate-400 hover:text-slate-600"/></button>
        </div>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-slate-500 block text-xs uppercase mb-1">操作时间</span>
              <span className="font-mono text-slate-800">{log.time}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-xs uppercase mb-1">操作人</span>
              <span className="font-medium text-slate-800">{log.user}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-xs uppercase mb-1">动作类型</span>
              <span className="font-medium text-blue-600">{log.action}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-xs uppercase mb-1">状态</span>
              <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${log.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                {log.status}
              </span>
            </div>
          </div>
          <div className="bg-slate-50 p-4 rounded border border-slate-200 font-mono text-sm text-slate-600">
            {log.detail}
            <br/>
            <span className="text-xs text-slate-400 mt-2 block">Trace ID: req_8d9a7f8c92b1</span>
          </div>
        </div>
        <div className="mt-6 flex justify-end">
          <button onClick={onClose} className="px-4 py-2 text-sm bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg">关闭</button>
        </div>
      </div>
    </div>
  );
};

const UserInfoEditModal = ({ onClose, currentUserRole }) => {
    return (
      <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
        <div className="bg-white rounded-xl shadow-2xl w-[500px] p-6 animate-in zoom-in-95 duration-200 relative">
          <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600">
            <X size={20} />
          </button>
          <h3 className="text-lg font-bold text-slate-800 mb-6">个人基本信息</h3>
          
          <div className="space-y-4">
             <div className="flex items-center gap-4 mb-6">
                <div className={`w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-bold ${currentUserRole === 'admin' ? 'bg-blue-600' : 'bg-green-500'}`}>
                   <User size={40}/>
                </div>
                <div>
                   <div className="text-sm text-slate-500 mb-1">当前角色</div>
                   <div className="font-bold text-slate-800">{currentUserRole === 'admin' ? '系统管理员' : '普通员工'}</div>
                </div>
             </div>

             <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1">用户昵称</label>
                    <input type="text" defaultValue={currentUserRole === 'admin' ? 'Admin' : 'User_001'} className="w-full border rounded p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
                </div>
                <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1">工号/ID</label>
                    <input type="text" defaultValue={currentUserRole === 'admin' ? 'AD_8829' : 'US_2048'} className="w-full border rounded p-2 text-sm bg-slate-50 text-slate-500" readOnly />
                </div>
             </div>
             
             <div>
                <label className="block text-xs font-bold text-slate-500 mb-1">手机号码</label>
                <input type="text" defaultValue="13800138000" className="w-full border rounded p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
             </div>
             
             <div>
                <label className="block text-xs font-bold text-slate-500 mb-1">电子邮箱</label>
                <input type="email" defaultValue="user@example.com" className="w-full border rounded p-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
             </div>
          </div>

          <div className="mt-8 flex justify-end gap-3">
             <button onClick={onClose} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded">取消</button>
             <button onClick={onClose} className="px-4 py-2 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded shadow-sm">保存修改</button>
          </div>
        </div>
      </div>
    );
};

// User Profile Menu (Dropdown Style)
const UserProfileMenu = ({ onClose, currentUserRole, onSwitchAccount, onSwitchRole, onLoginClick, onShowProfile }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-end bg-transparent" onClick={onClose}>
      <div 
         className="mt-16 mr-6 bg-white rounded-xl shadow-2xl w-[280px] p-4 animate-in fade-in slide-in-from-top-2 duration-200 border border-slate-100"
         onClick={e => e.stopPropagation()} 
      >
        <div className="flex items-center gap-3 mb-4 pb-4 border-b border-slate-100">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white shadow-sm ${currentUserRole === 'admin' ? 'bg-blue-600' : 'bg-green-500'}`}>
            <User size={20} />
          </div>
          <div>
              <h3 className="text-sm font-bold text-slate-800">{currentUserRole === 'admin' ? 'Administrator' : 'General User'}</h3>
              <p className="text-xs text-slate-500">ID: {currentUserRole === 'admin' ? 'AD_8829' : 'US_2048'}</p>
          </div>
        </div>

        <div className="space-y-1">
             {currentUserRole === 'admin' ? (
                <>
                  <button 
                    onClick={onLoginClick}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-slate-200 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors text-sm font-medium"
                  >
                    <RefreshCw size={16}/> 切换账号
                  </button>
                  <button 
                    onClick={onShowProfile}
                    className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-600 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-colors text-sm justify-center border border-transparent"
                  >
                    <Contact size={16}/> 个人信息
                  </button>
                  <button 
                    onClick={onSwitchRole}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
                  >
                    <LogOut size={16}/> 退出登录
                  </button>
                </>
             ) : (
                <>
                  <button 
                    onClick={onLoginClick}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shadow-sm"
                  >
                    <LogIn size={16}/> 切换账号
                  </button>
                  <button 
                    onClick={onShowProfile}
                    className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-600 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-colors text-sm justify-center"
                  >
                    <Contact size={16}/> 个人信息
                  </button>
                </>
             )}
        </div>
      </div>
    </div>
  );
};

const UnifiedUploadModal = ({ onClose, initialType = 'pdf' }) => {
    const [activeSkill, setActiveSkill] = useState('保养excel处理');
    
    const skills = [
      '保养excel处理',
      '保养pdf处理',
      '保用excel处理',
      '故障码excel处理',
      '故障灯图库处理',
      '用车功能pdf处理',
      '功能图库处理'
    ];
  
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
        <div className="bg-white rounded-xl shadow-2xl w-[800px] h-[500px] flex overflow-hidden animate-in zoom-in-95 duration-200">
          
          {/* Left Sidebar: Skill Selection */}
          <div className="w-64 bg-slate-50 border-r border-slate-200 flex flex-col">
             <div className="p-4 border-b border-slate-200 bg-slate-100/50">
               <h3 className="text-sm font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                 <Layers size={14}/> 处理策略 (Skill)
               </h3>
             </div>
             <div className="flex-1 overflow-y-auto p-3 space-y-1">
               {skills.map(skill => (
                 <button
                   key={skill}
                   onClick={() => setActiveSkill(skill)}
                   className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-all flex items-center justify-between group ${
                     activeSkill === skill 
                       ? 'bg-white text-blue-600 shadow-sm border border-blue-100' 
                       : 'text-slate-600 hover:bg-slate-200/50 hover:text-slate-900'
                   }`}
                 >
                   {skill}
                   {activeSkill === skill && <div className="w-1.5 h-1.5 rounded-full bg-blue-600"></div>}
                 </button>
               ))}
             </div>
          </div>
  
          {/* Right Content: Upload & Form */}
          <div className="flex-1 flex flex-col p-6 relative">
            <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1 rounded-full hover:bg-slate-100 transition-colors">
              <X size={20} />
            </button>
  
            <h3 className="text-lg font-semibold mb-6 flex items-center gap-2 text-slate-800">
              <Upload size={20} className="text-blue-600"/> 上传知识资产
            </h3>
            
            <div className="border-2 border-dashed border-slate-300 rounded-xl flex-1 flex flex-col items-center justify-center mb-6 bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer group border-spacing-4">
              <div className="w-14 h-14 bg-white rounded-full flex items-center justify-center shadow-sm mb-3 group-hover:scale-110 transition-transform border border-slate-100">
                 <Upload size={28} className="text-blue-500"/>
              </div>
              <p className="text-sm font-medium text-slate-700">点击或拖拽文件到此处</p>
              <p className="text-xs text-slate-400 mt-1">当前策略: <span className="text-blue-600 font-medium">{activeSkill}</span></p>
            </div>
  
            <div className="grid grid-cols-2 gap-5 mb-6">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5 ml-1">适用车型</label>
                <div className="relative">
                  <select className="w-full border border-slate-200 bg-slate-50 rounded-lg p-2.5 text-sm appearance-none focus:ring-2 focus:ring-blue-500 outline-none hover:border-slate-300 transition-colors">
                    <option>全部车型</option>
                    <option>一汽解放 J7</option>
                    <option>一汽解放 鹰途</option>
                    <option>J6P 系列</option>
                  </select>
                  <ChevronDown size={14} className="absolute right-3 top-3.5 text-slate-400 pointer-events-none"/>
                </div>
              </div>
  
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5 ml-1">模型选择</label>
                <div className="relative">
                  <select className="w-full border border-slate-200 bg-slate-50 rounded-lg p-2.5 text-sm appearance-none focus:ring-2 focus:ring-blue-500 outline-none hover:border-slate-300 transition-colors">
                    <option>Default (General)</option>
                    <option>GPT-4o</option>
                    <option>Claude 3.5 Sonnet</option>
                    <option>Qwen-Max (Long Context)</option>
                  </select>
                  <ChevronDown size={14} className="absolute right-3 top-3.5 text-slate-400 pointer-events-none"/>
                </div>
              </div>
            </div>
  
            <div className="flex justify-end gap-3 pt-2 border-t border-slate-100">
              <button onClick={onClose} className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">取消</button>
              <button onClick={onClose} className="px-6 py-2.5 text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 rounded-lg shadow-sm transition-colors flex items-center gap-2">
                <Upload size={16}/> 开始处理
              </button>
            </div>
          </div>
        </div>
      </div>
    );
};

const ErrorDetailModal = ({ doc, onClose }) => {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-lg shadow-xl w-[450px] overflow-hidden">
        <div className="bg-red-50 px-6 py-4 border-b border-red-100 flex justify-between items-center">
          <h3 className="font-bold text-red-700 flex items-center gap-2">
            <AlertTriangle size={20}/> 处理失败
          </h3>
          <button onClick={onClose} className="text-red-400 hover:text-red-600"><X size={20}/></button>
        </div>
        <div className="p-6">
          <p className="text-sm text-slate-600 mb-1">文件名称：</p>
          <p className="font-medium text-slate-800 mb-4">{doc.name}</p>
          
          <div className="bg-slate-50 border border-slate-200 rounded p-3 mb-6">
            <p className="text-xs text-slate-500 uppercase font-bold mb-1">失败原因 (Error Log)</p>
            <p className="text-sm text-red-600 font-mono break-all">{doc.failureReason || 'Unknown error occurred.'}</p>
          </div>

          <div className="flex justify-end gap-3">
            <button onClick={onClose} className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg">关闭</button>
            <button className="px-4 py-2 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded-lg shadow-sm flex items-center gap-2">
              <RefreshCw size={14}/> 重试处理
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Page Views ---

// 1. Dashboard View
const DashboardView = () => {
  return (
    <div className="flex flex-col h-full space-y-6">
      <section>
        <div className="flex items-center gap-2 mb-4">
          <PieChart className="text-blue-600" size={20} />
          <h2 className="text-lg font-bold text-slate-800">资产概览</h2>
          <span className="text-xs text-slate-400 ml-2">Asset Overview</span>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-100">
           <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2 mb-6">
             <Database size={16} className="text-slate-400"/> 数据总量统计
           </h3>
           <div className="flex flex-col md:flex-row gap-8">
              <div className="flex-1 grid grid-cols-3 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 flex flex-col justify-center">
                  <div className="flex items-center gap-2 text-xs text-blue-600 font-bold mb-2"><FileText size={14}/> 文档 (PDF)</div>
                  <div className="text-2xl font-bold text-slate-800">1,240</div>
                  <div className="text-xs text-slate-500 mt-1">85k 切片</div>
                </div>
                <div className="bg-emerald-50 p-4 rounded-lg border border-emerald-100 flex flex-col justify-center">
                  <div className="flex items-center gap-2 text-xs text-emerald-600 font-bold mb-2"><Table size={14}/> 结构化 (Excel)</div>
                  <div className="text-2xl font-bold text-slate-800">356</div>
                  <div className="text-xs text-slate-500 mt-1">12.5k 记录</div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-100 flex flex-col justify-center">
                  <div className="flex items-center gap-2 text-xs text-purple-600 font-bold mb-2"><Image size={14}/> 图库 (Image)</div>
                  <div className="text-2xl font-bold text-slate-800">580</div>
                  <div className="text-xs text-slate-500 mt-1">2.3k 样本</div>
                </div>
              </div>
              <div className="flex-1 flex flex-col justify-center border-l border-slate-100 pl-8">
                 <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">数据类型占比</h4>
                 <div className="w-full h-4 bg-slate-100 rounded-full flex overflow-hidden mb-4">
                    <div className="h-full bg-blue-500" style={{ width: '57%' }} title="PDF: 57%"></div>
                    <div className="h-full bg-emerald-500" style={{ width: '16%' }} title="Excel: 16%"></div>
                    <div className="h-full bg-purple-500" style={{ width: '27%' }} title="Image: 27%"></div>
                 </div>
                 <div className="flex justify-between text-xs text-slate-600">
                    <div className="flex items-center gap-2">
                       <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                       <span>PDF (57%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                       <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                       <span>Excel (16%)</span>
                    </div>
                    <div className="flex items-center gap-2">
                       <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                       <span>Image (27%)</span>
                    </div>
                 </div>
              </div>
           </div>
        </div>
      </section>
      <section>
        <div className="flex items-center gap-2 mb-4">
          <Activity className="text-blue-600" size={20} />
          <h2 className="text-lg font-bold text-slate-800">流水线监控</h2>
          <span className="text-xs text-slate-400 ml-2">Pipeline Monitor</span>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-100 grid grid-cols-1 md:grid-cols-3 gap-6"> 
            <div className="flex flex-col gap-3 border-r border-slate-100 pr-6 h-full md:col-span-2">
               <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2"><Layers size={14}/> 实时任务队列</h4>
               <div className="flex-1 flex flex-col justify-center">
                 <div className="grid grid-cols-3 gap-4">
                   <div className="flex flex-col items-center justify-center p-3 bg-blue-50 rounded-lg border border-blue-100">
                     <span className="flex items-center gap-2 text-xs font-bold text-blue-600 mb-1"><RefreshCcw size={14} className="animate-spin"/> 处理中</span>
                     <div className="text-2xl font-bold text-slate-800">12</div>
                     <div className="text-[10px] text-slate-500 mt-0.5">Files Processing</div>
                   </div>
                   <div className="flex flex-col items-center justify-center p-3 bg-purple-50 rounded-lg border border-purple-100">
                     <span className="flex items-center gap-2 text-xs font-bold text-purple-600 mb-1"><FileText size={14}/> 待审核</span>
                     <div className="text-2xl font-bold text-slate-800">5</div>
                     <div className="text-[10px] text-slate-500 mt-0.5">Pending Review</div>
                   </div>
                   <div className="flex flex-col items-center justify-center p-3 bg-red-50 rounded-lg border border-red-100">
                     <span className="flex items-center gap-2 text-xs font-bold text-red-600 mb-1"><AlertCircle size={14}/> 任务失败</span>
                     <div className="text-2xl font-bold text-slate-800">3</div>
                     <div className="text-[10px] text-slate-500 mt-0.5">Failed Jobs</div>
                   </div>
                 </div>
               </div>
            </div>
            <div className="flex flex-col gap-3 pl-2 h-full md:col-span-1">
               <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2"><Wrench size={14}/> Skills 管理</h4>
               <div className="overflow-y-auto h-[120px] pr-2 space-y-2 custom-scrollbar">
                 {MOCK_SKILLS.map((skill, idx) => (
                    <div key={idx} className="flex justify-between items-center text-xs p-2 bg-slate-50 rounded border border-slate-100 hover:border-blue-200 transition-colors">
                      <span className="text-slate-600">{skill.name}</span>
                      <span className={`flex items-center gap-1 text-[10px] uppercase font-bold px-1.5 py-0.5 rounded-full ${skill.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-500'}`}>
                        {skill.status}
                      </span>
                    </div>
                 ))}
               </div>
            </div>
        </div>
      </section>
      <section className="flex-1">
        <div className="flex items-center gap-2 mb-4">
          <History className="text-slate-500" size={20} />
          <h2 className="text-lg font-bold text-slate-800">最近操作日志</h2>
          <span className="text-xs text-slate-400 ml-2">System Activity</span>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-slate-100 overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 border-b border-slate-100">
               <tr>
                 <th className="p-3 font-medium pl-6">时间</th>
                 <th className="p-3 font-medium">操作人</th>
                 <th className="p-3 font-medium">动作</th>
                 <th className="p-3 font-medium">对象</th>
                 <th className="p-3 font-medium">状态</th>
               </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
               {MOCK_LOGS.map(log => (
                 <tr key={log.id} className="hover:bg-slate-50">
                    <td className="p-3 pl-6 text-slate-500 font-mono text-xs">{log.time}</td>
                    <td className="p-3 text-slate-700">{log.user}</td>
                    <td className="p-3 font-medium text-slate-800">{log.action}</td>
                    <td className="p-3 text-slate-500">{log.target}</td>
                    <td className="p-3">
                      {log.status === 'success' ? (
                        <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded border border-green-100">成功</span>
                      ) : (
                        <span className="text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded border border-amber-100">警告</span>
                      )}
                    </td>
                 </tr>
               ))}
            </tbody>
          </table>
          <div className="p-2 bg-slate-50 border-t border-slate-100 text-center">
             <button className="text-xs text-slate-500 hover:text-blue-600">查看更多日志</button>
          </div>
        </div>
      </section>
    </div>
  );
};

// 2. File Management View
const FileManagementView = ({ type, data, currentUserRole }) => {
  const [drawerType, setDrawerType] = useState(null); 
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [selectedImageItem, setSelectedImageItem] = useState(null); 
  const [excelRows, setExcelRows] = useState(MOCK_EXCEL_ROWS);
  const [imageItems, setImageItems] = useState(MOCK_IMAGE_ITEMS);
  const isReviewMode = drawerType === 'review';

  const handleRowClick = (doc) => {
    if (doc.status === 'processing') return; 
    setSelectedDoc(doc);
    setExcelRows(MOCK_EXCEL_ROWS);
    setImageItems(MOCK_IMAGE_ITEMS);
    if (doc.status === 'ready') setDrawerType('chunk');
    else if (doc.status === 'pending_review') setDrawerType('review');
    else if (doc.status === 'error') setDrawerType('error');
  };

  const closeDrawer = () => { setDrawerType(null); setSelectedDoc(null); setSelectedImageItem(null); };
  const handleImageClick = (item) => setSelectedImageItem(item);
  const handleBackToGallery = () => setSelectedImageItem(null);

  const handleAddExcelRow = () => {
    const newId = (parseInt(excelRows[excelRows.length - 1].id) + 1).toString().padStart(3, '0');
    setExcelRows([...excelRows, { id: newId, name: '', code: '', desc: '', cause: '', solution: '' }]);
  };
  const handleDeleteExcelRow = (index) => {
    const newRows = [...excelRows]; newRows.splice(index, 1); setExcelRows(newRows);
  };
  const handleAddImageItem = () => {
    const newId = imageItems[imageItems.length - 1].id + 1;
    setImageItems([...imageItems, { id: newId, name: 'New Image', src: 'placeholder', color: 'gray', desc: '', cause: '', solution: '' }]);
  };
  const handleDeleteImageItem = (e, id) => {
    e.stopPropagation(); setImageItems(imageItems.filter(item => item.id !== id));
  };

  return (
    <div className="flex flex-col h-full animate-in fade-in zoom-in-95 duration-200">
      <div className="bg-white rounded-lg shadow-sm flex-1 overflow-hidden flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 border-b border-slate-100">
              <tr>
                <th className="p-4 font-medium">文件名</th>
                <th className="p-4 font-medium">类型</th>
                <th className="p-4 font-medium">关联车型</th>
                <th className="p-4 font-medium">分类</th>
                <th className="p-4 font-medium">切片数</th>
                <th className="p-4 font-medium">大小/时间</th>
                <th className="p-4 font-medium">状态</th>
                <th className="p-4 font-medium text-right">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {data.map(doc => (
                <tr key={doc.id} className="hover:bg-slate-50 group transition-colors">
                  <td className="p-4 cursor-pointer" onClick={() => handleRowClick(doc)}>
                    <div className="font-medium text-slate-900 flex items-center gap-2">
                      {doc.type === 'pdf' && <FileText size={16} className="text-red-400"/>}
                      {doc.type === 'doc' && <FileText size={16} className="text-blue-400"/>}
                      {doc.type === 'excel' && <Table size={16} className="text-emerald-500"/>}
                      {doc.type === 'image' && <Image size={16} className="text-purple-500"/>}
                      {doc.name}
                    </div>
                  </td>
                  <td className="p-4"><span className="text-xs text-slate-400 uppercase">{doc.type}</span></td>
                  <td className="p-4"><span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-xs">{doc.model}</span></td>
                  <td className="p-4"><span className="border border-blue-100 text-blue-600 px-2 py-0.5 rounded text-xs">{doc.category}</span></td>
                  <td className="p-4 text-slate-500">{doc.chunks}</td>
                  <td className="p-4 text-xs text-slate-500"><div>{doc.size}</div><div>{doc.time}</div></td>
                  <td className="p-4"><StatusBadge status={doc.status} /></td>
                  <td className="p-4 text-right">
                    <div className="flex justify-end gap-3 opacity-0 group-hover:opacity-100 transition-opacity">
                      {doc.status !== 'processing' && (
                        <button onClick={() => handleRowClick(doc)} className="text-blue-600 hover:text-blue-800 font-medium text-xs">
                          {doc.status === 'ready' ? '预览' : doc.status === 'pending_review' ? '审核' : '错误详情'}
                        </button>
                      )}
                      {currentUserRole === 'admin' && <button className="text-red-500 hover:text-red-700"><Trash2 size={14}/></button>}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {(drawerType === 'chunk' || drawerType === 'review') && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-black/20" onClick={closeDrawer}></div>
          <div className="relative w-[900px] bg-white shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
            <div className="h-14 border-b flex items-center justify-between px-6 bg-slate-50">
              <div className="flex items-center gap-2">
                {isReviewMode ? <FileText className="text-purple-600" size={20}/> : <Eye className="text-blue-600" size={20}/>}
                <h3 className="font-semibold text-slate-800">{isReviewMode ? '人工审核' : '资产预览'}: {selectedDoc?.name}</h3>
              </div>
              <div className="flex items-center gap-2">
                {isReviewMode && (
                  <button onClick={closeDrawer} className="px-3 py-1.5 bg-green-600 text-white text-xs rounded hover:bg-green-700 flex items-center gap-1 shadow-sm"><CheckCircle size={12}/> 审核通过</button>
                )}
                <button onClick={closeDrawer} className="p-2 hover:bg-slate-200 rounded-full"><X size={18}/></button>
              </div>
            </div>
            <div className="flex-1 flex overflow-hidden">
              {selectedDoc?.type === 'image' ? (
                <div className="flex-1 flex flex-col overflow-hidden bg-slate-50">
                  {selectedImageItem ? (
                    <div className="flex-1 flex flex-col bg-white animate-in slide-in-from-right duration-200">
                      <div className="p-4 border-b flex items-center gap-2">
                        <button onClick={handleBackToGallery} className="p-1.5 hover:bg-slate-100 rounded-full text-slate-500"><ChevronLeft size={20}/></button>
                        <span className="font-bold text-slate-800">详情: {selectedImageItem.name}</span>
                      </div>
                      <div className="flex-1 overflow-y-auto p-8">
                        <div className="flex gap-8 items-start">
                          <div className="w-1/3 bg-slate-100 rounded-lg p-8 flex items-center justify-center border border-slate-200">
                             <div className={`w-32 h-32 rounded-full flex items-center justify-center ${selectedImageItem.color === 'red' ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'}`}><AlertCircle size={64}/></div>
                          </div>
                          <div className="flex-1 space-y-6">
                             {isReviewMode ? (
                               <>
                                <div className="grid grid-cols-2 gap-4">
                                   <div className="space-y-1.5"><label className="text-xs font-semibold text-slate-500">图标名称</label><input type="text" className="w-full border border-slate-300 rounded p-2 text-sm" defaultValue={selectedImageItem.name} /></div>
                                   <div className="space-y-1.5"><label className="text-xs font-semibold text-slate-500">颜色分类</label><select className="w-full border border-slate-300 rounded p-2 text-sm" defaultValue={selectedImageItem.color}><option value="red">红色 (Red)</option><option value="yellow">黄色 (Yellow)</option><option value="green">绿色 (Green)</option></select></div>
                                </div>
                                <div className="space-y-1.5"><label className="text-xs font-semibold text-slate-500">图标描述</label><textarea className="w-full border border-slate-300 rounded p-2 text-sm h-20 resize-none" defaultValue={selectedImageItem.desc} /></div>
                                <div className="space-y-1.5"><label className="text-xs font-semibold text-slate-500 flex items-center gap-1 text-red-500"><AlertTriangle size={12}/> 故障原因</label><textarea className="w-full border border-red-200 bg-red-50/30 rounded p-2 text-sm h-24 resize-none" defaultValue={selectedImageItem.cause} /></div>
                                <div className="space-y-1.5"><label className="text-xs font-semibold text-slate-500 flex items-center gap-1 text-blue-500"><CheckCircle size={12}/> 维修建议</label><textarea className="w-full border border-blue-200 bg-blue-50/30 rounded p-2 text-sm h-24 resize-none" defaultValue={selectedImageItem.solution} /></div>
                               </>
                             ) : (
                               <>
                                 <div><label className="text-xs font-bold text-slate-400 uppercase">故障描述</label><div className="text-lg font-medium text-slate-800 mt-1">{selectedImageItem.desc}</div></div>
                                 <div className="bg-red-50 p-4 rounded-lg border border-red-100"><label className="text-xs font-bold text-red-500 uppercase flex items-center gap-1"><AlertTriangle size={12}/> 故障原因</label><div className="text-sm text-red-800 mt-1">{selectedImageItem.cause}</div></div>
                                 <div className="bg-blue-50 p-4 rounded-lg border border-blue-100"><label className="text-xs font-bold text-blue-500 uppercase flex items-center gap-1"><CheckCircle size={12}/> 维修指导建议</label><div className="text-sm text-blue-800 mt-1">{selectedImageItem.solution}</div></div>
                               </>
                             )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex-1 overflow-y-auto p-6">
                      <div className="grid grid-cols-4 gap-4">
                        {imageItems.map(item => (
                          <div key={item.id} onClick={() => handleImageClick(item)} className="bg-white rounded-lg border border-slate-200 hover:shadow-md cursor-pointer transition-all hover:border-blue-400 group overflow-hidden relative">
                            {isReviewMode && <button onClick={(e) => handleDeleteImageItem(e, item.id)} className="absolute top-2 right-2 p-1.5 bg-red-100 text-red-600 rounded-full opacity-0 group-hover:opacity-100 z-10 hover:bg-red-200"><X size={14}/></button>}
                            <div className="aspect-square bg-slate-100 flex items-center justify-center p-4"><div className={`w-12 h-12 rounded-full flex items-center justify-center ${item.color === 'red' ? 'bg-red-100 text-red-500' : 'bg-yellow-100 text-yellow-600'}`}><AlertCircle size={24}/></div></div>
                            <div className="p-3 border-t border-slate-100 bg-white"><div className="text-xs font-mono text-slate-400 mb-1">#{item.id}</div><div className="text-sm font-medium text-slate-700 truncate group-hover:text-blue-600">{item.name}</div></div>
                          </div>
                        ))}
                        {isReviewMode && <button onClick={handleAddImageItem} className="aspect-square rounded-lg border-2 border-dashed border-slate-300 flex flex-col items-center justify-center text-slate-400 hover:text-blue-600 hover:border-blue-400 hover:bg-blue-50 transition-colors"><Plus size={32}/><span className="text-xs mt-2 font-medium">Add New Image</span></button>}
                      </div>
                    </div>
                  )}
                </div>
              ) : selectedDoc?.type === 'excel' ? (
                <div className="flex-1 flex flex-col bg-white">
                   {isReviewMode && <div className="p-2 bg-yellow-50 border-b border-yellow-100 text-xs text-yellow-700 px-4 flex items-center gap-2"><AlertCircle size={12}/> 请直接在表格中修改OCR识别错误的数据单元格。</div>}
                   <div className="flex-1 overflow-auto p-4">
                      <table className="w-full text-left text-sm border-collapse border border-slate-200">
                        <thead className="bg-slate-50 text-slate-700 sticky top-0 z-10 shadow-sm">
                          <tr>
                            <th className="border border-slate-300 p-2 w-12 text-center bg-slate-100">#</th>
                            <th className="border border-slate-300 p-2 min-w-[100px]">故障名称</th>
                            <th className="border border-slate-300 p-2 min-w-[80px]">代码</th>
                            <th className="border border-slate-300 p-2 min-w-[200px]">描述</th>
                            <th className="border border-slate-300 p-2 min-w-[200px]">原因</th>
                            <th className="border border-slate-300 p-2 min-w-[200px]">解决方案</th>
                            {isReviewMode && <th className="border border-slate-300 p-2 w-10 text-center bg-slate-100">Op</th>}
                          </tr>
                        </thead>
                        <tbody>
                          {excelRows.map((row, index) => (
                            <tr key={index} className="group hover:bg-slate-50">
                              <td className="border border-slate-200 p-2 text-center text-slate-400 bg-slate-50 text-xs">{row.id}</td>
                              {isReviewMode ? (
                                <>
                                  <td className="border border-slate-200 p-0"><input type="text" className="w-full h-full p-2 outline-none focus:bg-blue-50" defaultValue={row.name}/></td>
                                  <td className="border border-slate-200 p-0"><input type="text" className="w-full h-full p-2 outline-none focus:bg-blue-50 font-mono text-red-600 font-bold" defaultValue={row.code}/></td>
                                  <td className="border border-slate-200 p-0"><input type="text" className="w-full h-full p-2 outline-none focus:bg-blue-50" defaultValue={row.desc}/></td>
                                  <td className="border border-slate-200 p-0"><input type="text" className="w-full h-full p-2 outline-none focus:bg-blue-50" defaultValue={row.cause}/></td>
                                  <td className="border border-slate-200 p-0"><input type="text" className="w-full h-full p-2 outline-none focus:bg-blue-50" defaultValue={row.solution}/></td>
                                  <td className="border border-slate-200 p-0 text-center"><button onClick={() => handleDeleteExcelRow(index)} className="p-2 text-slate-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"><X size={14}/></button></td>
                                </>
                              ) : (
                                <>
                                  <td className="border border-slate-200 p-2 font-medium text-slate-800">{row.name}</td>
                                  <td className="border border-slate-200 p-2 text-red-600 font-bold font-mono">{row.code}</td>
                                  <td className="border border-slate-200 p-2 text-slate-600">{row.desc}</td>
                                  <td className="border border-slate-200 p-2 text-slate-600">{row.cause}</td>
                                  <td className="border border-slate-200 p-2 text-slate-600">{row.solution}</td>
                                </>
                              )}
                            </tr>
                          ))}
                          {isReviewMode && <tr><td colSpan="7" className="p-2 border border-dashed border-slate-300 text-center"><button onClick={handleAddExcelRow} className="text-xs text-blue-600 font-medium hover:text-blue-800 flex items-center justify-center gap-1 w-full py-1"><Plus size={14}/> Add New Row</button></td></tr>}
                        </tbody>
                      </table>
                   </div>
                </div>
              ) : (
                <>
                  <div className="w-1/2 bg-slate-100 border-r flex flex-col">
                    <div className="p-2 border-b bg-white text-xs text-slate-500 font-bold text-center">原始文件预览</div>
                    <div className="flex-1 p-8 overflow-y-auto flex items-center justify-center">
                       <div className="w-full h-full bg-white shadow-sm border border-slate-200 p-8 flex flex-col items-center justify-center text-slate-400"><FileText size={64}/><p className="text-xs mt-2">Showing Page 1</p></div>
                    </div>
                  </div>
                  <div className="w-1/2 bg-white flex flex-col">
                    {isReviewMode ? (
                        <>
                            <div className="p-2 border-b bg-white text-xs text-slate-500 font-bold text-center flex justify-between px-4"><span>OCR 识别结果 (Markdown 编辑)</span><span className="text-blue-600 cursor-pointer">重置</span></div>
                            <div className="flex-1 p-0"><textarea className="w-full h-full p-6 text-sm font-mono text-slate-700 outline-none resize-none" defaultValue={selectedDoc?.markdownContent || "Mock content for review..."} /></div>
                        </>
                    ) : (
                        <>
                            <div className="p-4 border-b bg-white text-xs text-slate-500 font-bold">共解析出 {selectedDoc?.chunks || 0} 个切片</div>
                            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="border border-slate-200 rounded-lg p-3 hover:border-blue-400 hover:shadow-sm transition-all group">
                                    <div className="flex justify-between items-center mb-2"><span className="text-xs font-mono text-slate-400">ID: chunk_00{i}</span><span className="text-xs bg-slate-100 px-1.5 rounded text-slate-600">Page {i}</span></div>
                                    <div className="text-sm text-slate-700">这里是解析出来的文本切片内容示例 {i}。预览模式下不可直接修改。</div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
      {drawerType === 'error' && <ErrorDetailModal doc={selectedDoc} onClose={closeDrawer} />}
      {uploadModalOpen && <UnifiedUploadModal onClose={() => setUploadModalOpen(false)} initialType={type} />}
    </div>
  );
};

// 3. Sandbox View
const SandboxView = () => {
  const [messages, setMessages] = useState([
    { role: 'ai', text: '你好，我是智能诊断助手。请描述车辆遇到的问题，或上传故障图片。' }
  ]);
  const [input, setInput] = useState('');

  const sendMessage = () => {
    if(!input.trim()) return;
    setMessages([...messages, { role: 'user', text: input }]);
    setInput('');
    setTimeout(() => {
       setMessages(prev => [...prev, { role: 'ai', text: '根据您的描述，这可能是发动机随机失火（P0300）。我为您找到了相关的维修案例。' }]);
    }, 1500);
  };

  return (
    <div className="flex h-full gap-6">
      <div className="w-1/3 flex flex-col bg-white rounded-lg shadow-sm border border-slate-200">
        <div className="p-4 border-b bg-slate-50">
          <h3 className="font-semibold text-slate-700 flex items-center gap-2"><MessageSquare size={18}/> 模拟终端</h3>
          <div className="mt-3 flex gap-2">
            <select className="text-xs border rounded p-1 w-full"><option>模拟车型: J7</option></select>
            <select className="text-xs border rounded p-1 w-full"><option>身份: 车主</option></select>
          </div>
        </div>
        <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50">
          {messages.map((m, idx) => (
             <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-lg p-3 text-sm ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border text-slate-700 shadow-sm'}`}>
                  {m.text}
                </div>
             </div>
          ))}
        </div>
        <div className="p-3 border-t bg-white">
          <div className="relative">
            <input 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              className="w-full border rounded-lg pl-3 pr-10 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none" 
              placeholder="输入测试问题..." 
            />
            <button onClick={sendMessage} className="absolute right-2 top-2 text-blue-600"><ArrowRight size={18}/></button>
          </div>
          <div className="mt-2 flex justify-between items-center text-xs text-slate-400">
            <button className="flex items-center gap-1 hover:text-slate-600"><Image size={14}/> 上传图片</button>
            <span>Enter 发送</span>
          </div>
        </div>
      </div>
      <div className="flex-1 flex flex-col gap-4 overflow-y-auto">
        <div className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-purple-500">
           <h4 className="text-xs font-bold text-slate-400 uppercase mb-2 flex items-center gap-2"><Cpu size={14}/> 意图识别 (NLU)</h4>
           <div className="flex gap-4 text-sm">
             <div className="bg-purple-50 text-purple-700 px-3 py-1 rounded">Intent: <span className="font-mono font-bold">Fault_Query</span></div>
             <div className="bg-slate-100 text-slate-700 px-3 py-1 rounded">Entities: <span className="font-mono">['Engine', 'Noise']</span></div>
           </div>
        </div>
        <div className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-amber-500 flex-1">
           <h4 className="text-xs font-bold text-slate-400 uppercase mb-3 flex items-center gap-2"><Database size={14}/> 知识召回 (RAG Retrieval)</h4>
           <div className="space-y-3">
             {[1, 2].map(i => (
               <div key={i} className="p-3 border border-slate-100 rounded hover:bg-slate-50">
                 <div className="flex justify-between mb-1">
                   <span className="text-xs font-bold text-slate-600">SOURCE: 发动机维修手册_V2.pdf (Page 45)</span>
                   <span className="text-xs font-mono text-green-600">Score: 0.9{5-i}</span>
                 </div>
                 <p className="text-xs text-slate-500 line-clamp-2">...当检测到气缸失火时，ECU会记录P0300代码。可能的原因包括点火线圈老化、火花塞间隙过大或燃油喷射嘴堵塞...</p>
               </div>
             ))}
           </div>
        </div>
        <div className="bg-white rounded-lg p-4 shadow-sm border-l-4 border-blue-500">
           <h4 className="text-xs font-bold text-slate-400 uppercase mb-2 flex items-center gap-2"><MessageSquare size={14}/> 最终生成 (LLM Generation)</h4>
           <p className="text-sm text-slate-700 leading-relaxed">
             根据您的描述，这可能是发动机随机失火（P0300）。我为您找到了相关的维修案例。建议优先检查点火线圈和火花塞。
           </p>
        </div>
      </div>
    </div>
  );
};

// 4. RLHF View
const RLHFView = () => {
  const [activeTab, setActiveTab] = useState('pending');
  const [selectedFeedback, setSelectedFeedback] = useState(null);

  // Filter data based on active tab
  const filteredData = MOCK_RLHF.filter(item => {
    if (activeTab === 'pending') return item.status === 'pending';
    if (activeTab === 'processed') return item.status === 'processed';
    if (activeTab === 'ignored') return item.status === 'ignored';
    return true;
  });

  return (
    <div className="flex flex-col h-full">
      <div className="bg-white p-4 rounded-lg shadow-sm mb-4">
        <div className="flex gap-2 text-sm">
          <button 
            onClick={() => { setActiveTab('pending'); setSelectedFeedback(null); }}
            className={`px-3 py-1.5 rounded transition-colors ${activeTab === 'pending' ? 'bg-slate-800 text-white' : 'text-slate-600 hover:bg-slate-100'}`}
          >
            待处理
          </button>
          <button 
            onClick={() => { setActiveTab('processed'); setSelectedFeedback(null); }}
            className={`px-3 py-1.5 rounded transition-colors ${activeTab === 'processed' ? 'bg-slate-800 text-white' : 'text-slate-600 hover:bg-slate-100'}`}
          >
            已入库
          </button>
          <button 
            onClick={() => { setActiveTab('ignored'); setSelectedFeedback(null); }}
            className={`px-3 py-1.5 rounded transition-colors ${activeTab === 'ignored' ? 'bg-slate-800 text-white' : 'text-slate-600 hover:bg-slate-100'}`}
          >
            已忽略
          </button>
        </div>
      </div>
      <div className="flex h-full gap-4 overflow-hidden">
        <div className="w-1/2 bg-white rounded-lg shadow-sm overflow-y-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 sticky top-0">
              <tr>
                <th className="p-3 text-xs font-medium text-slate-500">用户问题</th>
                {activeTab === 'pending' && <th className="p-3 text-xs font-medium text-slate-500 w-32">反馈原因</th>}
                <th className="p-3 text-xs font-medium text-slate-500 w-32 text-right">时间</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredData.map(item => (
                <tr key={item.id} onClick={() => setSelectedFeedback(item)} className={`cursor-pointer hover:bg-blue-50 transition-colors ${selectedFeedback?.id === item.id ? 'bg-blue-50' : ''}`}>
                  <td className="p-3">
                    <div className="font-medium text-slate-800 mb-1">{item.userQ}</div>
                    <div className="text-xs text-slate-400 truncate max-w-[300px]">AI: {item.aiAns}</div>
                  </td>
                  {activeTab === 'pending' && (
                    <td className="p-3 text-xs text-red-600 font-medium">
                      {item.reason}
                    </td>
                  )}
                  <td className="p-3 text-right text-xs text-slate-400">
                     {item.date.split(' ')[0]}
                  </td>
                </tr>
              ))}
              {filteredData.length === 0 && (
                <tr>
                    <td colSpan="3" className="p-8 text-center text-slate-400 text-xs">暂无数据</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="w-1/2 bg-white rounded-lg shadow-sm p-6 flex flex-col">
          {selectedFeedback ? (
            <>
              <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
                 <GitCommit size={20}/> 
                 {activeTab === 'pending' ? '修正反馈详情' : activeTab === 'processed' ? '入库详情' : '忽略详情'}
              </h3>
              <div className="flex-1 space-y-6">
                <div>
                  <label className="text-xs font-bold text-slate-400 uppercase">User Query</label>
                  <div className="bg-slate-50 p-3 rounded mt-1 text-sm">{selectedFeedback.userQ}</div>
                </div>
                
                {activeTab === 'ignored' ? (
                   <div className="p-4 bg-gray-50 border border-gray-100 rounded text-sm text-slate-600">
                      <span className="font-bold">忽略原因：</span> {selectedFeedback.reason || '未填写原因'}
                   </div>
                ) : activeTab === 'processed' ? (
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 border border-slate-200 bg-slate-50 rounded">
                            <label className="text-xs font-bold text-slate-500 uppercase mb-2 block">原文档内容 (Original)</label>
                            <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{selectedFeedback.originalDoc}</p>
                        </div>
                        <div className="p-3 border border-green-200 bg-green-50/50 rounded">
                            <label className="text-xs font-bold text-green-600 uppercase mb-2 block">入库文档内容 (Final)</label>
                            <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">{selectedFeedback.modifiedDoc}</p>
                        </div>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 border border-red-200 bg-red-50/50 rounded">
                            <label className="text-xs font-bold text-red-500 uppercase mb-2 block">Original AI (Bad)</label>
                            <p className="text-sm text-slate-700">{selectedFeedback.aiAns}</p>
                        </div>
                        <div className="p-3 border border-green-200 bg-green-50/50 rounded">
                            <label className="text-xs font-bold text-green-600 uppercase mb-2 block">Human Agent (Good)</label>
                            <p className="text-sm text-slate-700">{selectedFeedback.agentAns}</p>
                        </div>
                    </div>
                )}

                {activeTab === 'pending' && (
                    <div className="pt-6 border-t mt-4">
                    <label className="text-xs font-bold text-slate-400 uppercase mb-3 block">采取行动</label>
                    <div className="flex gap-3">
                        <button className="flex-1 border border-slate-200 p-3 rounded hover:bg-slate-50 flex items-center justify-center gap-2 text-sm font-medium text-slate-700">
                        <FileText size={16}/> 修正源文档切片
                        </button>
                        <button className="flex-1 bg-blue-600 text-white p-3 rounded hover:bg-blue-700 flex items-center justify-center gap-2 text-sm font-medium shadow-md">
                        <CheckCircle size={16}/> 存为标准问答对
                        </button>
                    </div>
                    </div>
                )}
              </div>
            </>
          ) : (
             <div className="flex items-center justify-center h-full text-slate-400 text-sm">
               Select an item to review
             </div>
          )}
        </div>
      </div>
    </div>
  );
};

// 5. Settings View (UPDATED LOGIC)
const SettingsView = () => {
  const [activeTab, setActiveTab] = useState('business');
  
  // State for Business Dictionary Edit Mode
  const [isEditingBusiness, setIsEditingBusiness] = useState(false);
  
  // State for User Management
  const [showAddUser, setShowAddUser] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  // State for Logs
  const [selectedLog, setSelectedLog] = useState(null);

  const tabs = [
    { id: 'business', label: '业务字典配置', icon: BookOpen },
    { id: 'users', label: '用户与权限', icon: User },
    { id: 'ops', label: '系统运维监控', icon: Activity },
  ];

  return (
    <div className="flex h-full gap-6">
      <div className="w-64 flex flex-col bg-white rounded-lg shadow-sm border border-slate-200 h-fit">
        <div className="p-4 border-b border-slate-100">
          <h3 className="font-bold text-slate-800">系统设置</h3>
        </div>
        <div className="p-2 space-y-1">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab.id 
                  ? 'bg-blue-50 text-blue-700' 
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <tab.icon size={18} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 bg-white rounded-lg shadow-sm border border-slate-200 p-8 overflow-y-auto">
        
        {/* Tab 1: Business Dictionary */}
        {activeTab === 'business' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-lg font-bold text-slate-800 mb-1">业务字典配置</h2>
                <p className="text-sm text-slate-500">管理车型层级结构及功能板块定义。</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-8">
              {/* Vehicle Hierarchy */}
              <div className="border border-slate-200 rounded-lg overflow-hidden relative">
                <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex justify-between items-center">
                  <h3 className="font-bold text-sm text-slate-700">车型/车系管理</h3>
                  <button 
                    onClick={() => setIsEditingBusiness(!isEditingBusiness)}
                    className={`text-xs px-2 py-1 rounded border ${isEditingBusiness ? 'bg-blue-100 text-blue-700 border-blue-200' : 'bg-white text-slate-500 border-slate-200'}`}
                  >
                    {isEditingBusiness ? '完成' : '修改'}
                  </button>
                </div>
                <div className="p-4 h-[300px] overflow-y-auto">
                   <div className="space-y-3">
                      <div className="flex items-center justify-between">
                         <span className="text-sm font-medium text-slate-800 flex items-center gap-2"><ChevronDown size={14}/> 一汽解放</span>
                         {isEditingBusiness && <div className="flex gap-1"><button className="text-blue-600"><Plus size={14}/></button></div>}
                      </div>
                      <div className="pl-6 space-y-2">
                         {['J6P 系列', 'J7 系列'].map(series => (
                           <div key={series} className="flex items-center justify-between group">
                              <span className="text-sm text-slate-600">{series}</span>
                              {isEditingBusiness && (
                                <div className="flex gap-2 opacity-100">
                                   <button className="text-blue-500 hover:text-blue-700"><Edit3 size={12}/></button>
                                   <button className="text-red-500 hover:text-red-700"><Trash2 size={12}/></button>
                                </div>
                              )}
                           </div>
                         ))}
                      </div>
                   </div>
                   {isEditingBusiness && (
                     <div className="mt-4 pt-4 border-t border-dashed text-center">
                       <button className="text-xs text-blue-600 flex items-center justify-center gap-1 w-full"><Plus size={14}/> 新增品牌</button>
                     </div>
                   )}
                </div>
              </div>

              {/* Functional Sections */}
              <div className="border border-slate-200 rounded-lg overflow-hidden">
                <div className="bg-slate-50 px-4 py-3 border-b border-slate-200 flex justify-between items-center">
                  <h3 className="font-bold text-sm text-slate-700">功能板块定义</h3>
                  <button 
                    onClick={() => setIsEditingBusiness(!isEditingBusiness)}
                    className={`text-xs px-2 py-1 rounded border ${isEditingBusiness ? 'bg-blue-100 text-blue-700 border-blue-200' : 'bg-white text-slate-500 border-slate-200'}`}
                  >
                    {isEditingBusiness ? '完成' : '修改'}
                  </button>
                </div>
                <div className="divide-y divide-slate-100">
                  {['保用手册', '维修保养', '故障代码', '功能说明'].map((sec, i) => (
                    <div key={i} className="px-4 py-3 flex items-center justify-between group">
                      <span className="text-sm text-slate-700">{sec}</span>
                      {isEditingBusiness && (
                        <div className="flex gap-2">
                           <button className="text-blue-500"><Edit3 size={14}/></button>
                           <button className="text-red-500"><Trash2 size={14}/></button>
                        </div>
                      )}
                    </div>
                  ))}
                  {isEditingBusiness && (
                     <div className="p-3 text-center">
                       <button className="text-xs text-blue-600 flex items-center justify-center gap-1 w-full"><Plus size={14}/> 新增板块</button>
                     </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: User Management */}
        {activeTab === 'users' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-lg font-bold text-slate-800 mb-1">用户与权限管理</h2>
                <p className="text-sm text-slate-500">管理后台账号及角色权限。</p>
              </div>
              <button 
                onClick={() => setShowAddUser(true)}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 flex items-center gap-2"
              >
                <UserPlus size={16}/> 新增用户
              </button>
            </div>
            <div className="border border-slate-200 rounded-lg overflow-hidden">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                  <tr>
                    <th className="p-4 font-medium">用户名</th>
                    <th className="p-4 font-medium">角色</th>
                    <th className="p-4 font-medium">状态</th>
                    <th className="p-4 font-medium text-right">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {MOCK_USERS.map(user => (
                    <tr key={user.id} className="hover:bg-slate-50">
                      <td className="p-4">
                        <div className="font-medium text-slate-800">{user.name}</div>
                        <div className="text-xs text-slate-400">{user.email}</div>
                      </td>
                      <td className="p-4">
                        <span className="px-2 py-1 rounded text-xs bg-slate-100 text-slate-600 border border-slate-200">{user.role}</span>
                      </td>
                      <td className="p-4">
                        <span className="text-green-600 text-xs font-medium">{user.status}</span>
                      </td>
                      <td className="p-4 text-right">
                        <button 
                          onClick={() => setEditingUser(user)}
                          className="text-blue-600 hover:text-blue-800 text-xs font-medium border border-blue-200 px-3 py-1 rounded hover:bg-blue-50"
                        >
                          修改
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: System Ops Monitoring (Logs Only) */}
        {activeTab === 'ops' && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div>
              <h2 className="text-lg font-bold text-slate-800 mb-1">系统运维监控</h2>
              <p className="text-sm text-slate-500">查看系统操作审计日志。</p>
            </div>
            
            {/* Audit Logs Only - No Dangerous Ops */}
            <div className="border border-slate-200 rounded-lg overflow-hidden">
               <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                  <h3 className="font-bold text-sm text-slate-700">操作审计日志</h3>
               </div>
               <table className="w-full text-left text-sm">
                 <thead className="bg-white text-slate-500 border-b border-slate-100">
                   <tr>
                     <th className="p-3 pl-4 font-medium">时间</th>
                     <th className="p-3 font-medium">操作人</th>
                     <th className="p-3 font-medium">操作类型</th>
                     <th className="p-3 font-medium">详情</th>
                   </tr>
                 </thead>
                 <tbody className="divide-y divide-slate-50">
                   {MOCK_LOGS.map((log, i) => (
                     <tr 
                        key={i} 
                        onClick={() => setSelectedLog(log)}
                        className="hover:bg-blue-50 cursor-pointer transition-colors"
                     >
                       <td className="p-3 pl-4 text-slate-500 font-mono text-xs">{log.time}</td>
                       <td className="p-3 text-slate-700">{log.user}</td>
                       <td className="p-3"><span className="bg-slate-100 text-slate-600 px-2 py-0.5 rounded text-xs">{log.action}</span></td>
                       <td className="p-3 text-slate-600 truncate max-w-xs">{log.detail}</td>
                     </tr>
                   ))}
                 </tbody>
               </table>
            </div>
          </div>
        )}
      </div>

      {/* Settings Modals */}
      {showAddUser && <AddUserModal onClose={() => setShowAddUser(false)} />}
      {editingUser && <EditUserModal user={editingUser} onClose={() => setEditingUser(null)} />}
      {selectedLog && <LogDetailModal log={selectedLog} onClose={() => setSelectedLog(null)} />}
    </div>
  );
};
  
const KnowledgeBaseView = ({ currentUserRole }) => {
    const [activeTab, setActiveTab] = useState('pdf'); // pdf | excel | image
    const [uploadModalOpen, setUploadModalOpen] = useState(false);
  
    return (
      <div className="flex flex-col h-full">
        {/* Top Filters & Actions (Restored) */}
        <div className="bg-white p-4 rounded-lg shadow-sm mb-4 flex flex-wrap gap-4 items-end">
            <div>
              <label className="block text-xs text-slate-500 mb-1">适用车型</label>
              <select className="border border-slate-200 rounded px-3 py-1.5 text-sm w-32 focus:outline-none focus:border-blue-500 text-slate-700">
                  <option>全部</option>
                  <option>J7</option>
                  <option>鹰途</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-slate-500 mb-1">知识分类</label>
              <select className="border border-slate-200 rounded px-3 py-1.5 text-sm w-32 focus:outline-none focus:border-blue-500 text-slate-700">
                  <option>全部</option>
                  <option>保用</option>
                  <option>保养</option>
                  <option>故障</option>
                  <option>功能</option>
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-xs text-slate-500 mb-1">搜索文件</label>
              <div className="relative">
                  <Search size={16} className="absolute left-3 top-2 text-slate-400" />
                  <input type="text" placeholder={`搜索 ${activeTab === 'pdf' ? '文档' : activeTab === 'excel' ? '表格' : '图片'}...`} className="border border-slate-200 rounded pl-9 pr-3 py-1.5 text-sm w-full focus:outline-none focus:border-blue-500" />
              </div>
            </div>
            <div className="flex gap-2">
              <button className="bg-blue-600 text-white px-4 py-1.5 rounded text-sm hover:bg-blue-700 transition-colors">查询</button>
              <button className="border border-slate-200 text-slate-600 px-4 py-1.5 rounded text-sm hover:bg-slate-50 transition-colors">重置</button>
              <button 
                onClick={() => setUploadModalOpen(true)} 
                className="bg-indigo-600 text-white px-4 py-1.5 rounded text-sm hover:bg-indigo-700 flex items-center gap-1 ml-2 transition-colors"
              >
                  <Upload size={14}/> 上传文档
              </button>
            </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-4 flex space-x-1 bg-slate-100 p-1 rounded-lg w-fit">
          <button 
            onClick={() => setActiveTab('pdf')} 
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'pdf' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'}`}
          >
            <FileText size={14} />非结构化文档 (PDF)
          </button>
          <button 
            onClick={() => setActiveTab('excel')} 
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'excel' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'}`}
          >
            <Table size={14} />结构化数据 (Excel)
          </button>
          <button 
            onClick={() => setActiveTab('image')} 
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'image' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'}`}
          >
            <Image size={14} />图库 (Image)
          </button>
        </div>
  
        {/* Content Area - Now uses unified FileManagementView */}
        <div className="flex-1 overflow-hidden relative">
          {activeTab === 'pdf' && <FileManagementView type="pdf" data={MOCK_PDF_FILES} currentUserRole={currentUserRole} />}
          {activeTab === 'excel' && <FileManagementView type="excel" data={MOCK_EXCEL_FILES} currentUserRole={currentUserRole} />}
          {activeTab === 'image' && <FileManagementView type="image" data={MOCK_IMAGE_FILES} currentUserRole={currentUserRole} />}
        </div>

        {/* Upload Modal controlled by KnowledgeBaseView */}
        {uploadModalOpen && <UnifiedUploadModal onClose={() => setUploadModalOpen(false)} initialType={activeTab} />}
      </div>
    );
};
  
const App = () => {
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [currentUserRole, setCurrentUserRole] = useState('user'); // Default to 'user' now
    const [showLoginModal, setShowLoginModal] = useState(false);
    const [showUserModal, setShowUserModal] = useState(false); // Added missing state for UserProfileMenu
    const [showUserInfoModal, setShowUserInfoModal] = useState(false); // Added state for UserInfoEditModal
  
    const renderPage = () => {
      switch(currentPage) {
        case 'dashboard': return <DashboardView />;
        case 'knowledge': return <KnowledgeBaseView currentUserRole={currentUserRole} />; 
        case 'sandbox': return <SandboxView />;
        case 'rlhf': return <RLHFView />;
        case 'settings': return <SettingsView />; 
        default: return <DashboardView />;
      }
    };
  
    const handleSettingsClick = () => {
      if (currentUserRole !== 'admin') {
        setShowLoginModal(true);
      } else {
        setCurrentPage('settings');
      }
    };

    const handleLogin = () => {
       setCurrentUserRole('admin');
       setShowLoginModal(false);
       setCurrentPage('settings');
    };

    const handleLogout = () => {
      setCurrentUserRole('user');
      setShowUserModal(false);
      setCurrentPage('dashboard');
    };
  
    const getPageTitle = () => {
      const map = {
        'knowledge': '知识库中心',
        'sandbox': '测试沙箱 (SIT)',
        'rlhf': '问题反馈 (RLHF)',
        'dashboard': '工作台',
        'settings': '系统设置'
      };
      return map[currentPage] || '知识引擎';
    };
  
    return (
      <div className="flex h-screen bg-gray-50 font-sans text-slate-900">
        {/* Sidebar */}
        <aside className="w-64 bg-slate-900 text-white flex flex-col flex-shrink-0">
          <div className="h-16 flex items-center px-6 font-bold text-lg tracking-wide border-b border-slate-800">
            <div className="w-8 h-8 bg-blue-600 rounded mr-3 flex items-center justify-center">K</div>
            KNOWLEDGE
          </div>
          
          <div className="flex-1 py-4 space-y-1">
            <div className="px-4 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 mt-2">Main</div>
            <SidebarItem icon={LayoutDashboard} label="工作台" active={currentPage === 'dashboard'} onClick={() => setCurrentPage('dashboard')} />
            <div className="px-4 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 mt-6">Knowledge Base</div>
            <SidebarItem icon={Database} label="知识库管理" active={currentPage === 'knowledge'} onClick={() => setCurrentPage('knowledge')} />
            <div className="px-4 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2 mt-6">AI Ops</div>
            <SidebarItem icon={RefreshCcw} label="问题反馈" active={currentPage === 'rlhf'} onClick={() => setCurrentPage('rlhf')} />
          </div>
  
          <div className="p-4 border-t border-slate-800 space-y-2">
             {currentUserRole === 'admin' && (
               <SidebarItem icon={Settings} label="系统设置" active={currentPage === 'settings'} onClick={() => setCurrentPage('settings')} />
             )}
          </div>
        </aside>
  
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm z-10">
            <div className="flex items-center text-sm text-slate-500">
              <span className="hover:text-slate-800 cursor-pointer">首页</span>
              <ChevronRight size={16} className="mx-2"/>
              <span className="font-medium text-slate-800">{getPageTitle()}</span>
            </div>
            <div className="flex items-center gap-4">
               <div className="relative hidden md:block">
                 <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                 <input type="text" placeholder="全局搜索..." className="bg-slate-100 border-none rounded-full pl-9 pr-4 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 w-64" />
               </div>
               <button className="relative p-2 text-slate-500 hover:bg-slate-100 rounded-full">
                 <Bell size={20} />
                 <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
               </button>
               {/* Click Avatar to open simple User Profile Modal */}
               <div onClick={() => setShowUserModal(true)} className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-700 font-bold text-xs cursor-pointer hover:ring-2 ring-blue-300 transition-all">
                 {currentUserRole === 'admin' ? 'AD' : 'US'}
               </div>
            </div>
          </header>
  
          <main className="flex-1 overflow-auto p-6 relative bg-slate-50">
            {renderPage()}
          </main>
        </div>
  
        {showLoginModal && <LoginModal onClose={() => setShowLoginModal(false)} onLogin={handleLogin} />}
        {showUserInfoModal && <UserInfoEditModal onClose={() => setShowUserInfoModal(false)} currentUserRole={currentUserRole} />}
        {showUserModal && (
            <UserProfileMenu 
                onClose={() => setShowUserModal(false)} 
                currentUserRole={currentUserRole} 
                onSwitchAccount={() => {setShowUserModal(false); setShowLoginModal(true);}} 
                onShowProfile={() => {setShowUserModal(false); setShowUserInfoModal(true);}}
                onSwitchRole={handleLogout}
                onLoginClick={() => {setShowUserModal(false); setShowLoginModal(true);}}
            />
        )}
      </div>
    );
};

export default App;