import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import EquipmentLoanPage from '../pages/EquipmentLoanPage.jsx'

// test จาก specs/007-equipment/test-cases.md ห้ามแก้ให้ผ่าน
const STUDENTS = [{ student_id: '64000001', name: 'นักศึกษาทดสอบ' }]

function studentClient(items, createLoanRequest = vi.fn().mockResolvedValue({ request_id: 'REQ-0001', status: 'pending', quantity: 1 })) {
  return {
    listEquipmentTypes: vi.fn().mockResolvedValue({ items }),
    listStudents: vi.fn().mockResolvedValue({ items: STUDENTS }),
    createLoanRequest,
  }
}

async function renderStudentPage(client, firstName) {
  render(<EquipmentLoanPage client={client} />)
  if (firstName) await screen.findByText(firstName)
  await screen.findByRole('option', { name: /นักศึกษาทดสอบ/ })
}

const THREE_TYPES = [
  { equipment_type_id: 'EQ-PLUG', name: 'ปลั๊กไฟ', available_count: 4 },
  { equipment_type_id: 'EQ-UMBRELLA', name: 'ร่ม', available_count: 2 },
  { equipment_type_id: 'EQ-BAG', name: 'ถุงผ้า', available_count: 5 },
]

test('test_TC_EQP_03_4_stock_runs_out_after_page_load', async () => {
  // Given เปิดหน้าตอนร่มคงเหลือ 1 แล้วร่มถูกยืมจนหมด หลังบ้านจึงตอบว่า "ไม่สามารถยืมได้" (409)
  const items = THREE_TYPES.map((item) => (item.name === 'ร่ม' ? { ...item, available_count: 1 } : item))
  const client = studentClient(items, vi.fn().mockRejectedValue(new Error('Loan request failed: 409')))
  await renderStudentPage(client, 'ร่ม')

  // When นักศึกษากดส่งคำขอยืมร่ม
  fireEvent.click(screen.getByRole('button', { name: /ร่ม/ }))
  fireEvent.click(screen.getByRole('button', { name: 'ส่งคำขอยืม' }))
  await waitFor(() => expect(client.createLoanRequest).toHaveBeenCalled())

  // Then (1) หน้าจอแจ้งว่า "ไม่สามารถยืมได้"
  expect(await screen.findByText('ไม่สามารถยืมได้')).toBeTruthy()
  // (2) หน้าจอไม่แสดงว่าส่งคำขอแล้ว
  expect(screen.queryByText('ส่งคำขอแล้ว')).toBeNull()
})
