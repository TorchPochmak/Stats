#include <iostream>
#include <string>
#include <xlnt/xlnt.hpp>

void addData(xlnt::worksheet& ws, int row, int col, const std::string& data) {
    ws.cell(row, col).value(data);
}

void deleteData(xlnt::worksheet& ws, int row, int col) {
    ws.cell(row, col).clear();
}

void updateData(xlnt::worksheet& ws, int row, int col, const std::string& data) {
    ws.cell(row, col).value(data);
}

void calculateParameters(xlnt::worksheet& ws) {
    for (int row = 2; row <= ws.highest_row(); ++row) {
        double quantity = ws.cell(row, 2).value<double>();
        double purchase_price = ws.cell(row, 3).value<double>();
        double current_price = ws.cell(row, 4).value<double>();

        double investment_amount = quantity * purchase_price;
        double current_value = quantity * current_price;
        double profit_loss = current_value - investment_amount;
        double return_rate = (profit_loss / investment_amount) * 100;

        ws.cell(row, 5).value(investment_amount);
        ws.cell(row, 6).value(current_value);
        ws.cell(row, 7).value(profit_loss);
        ws.cell(row, 8).value(return_rate);
    }
}

int main() {
    xlnt::workbook wb;
    xlnt::worksheet ws;

    std::string filename;
    std::cout << "Enter the Excel file name (with .xlsx extension): ";
    std::cin >> filename;

    try {
        wb.load(filename);
        ws = wb.active_sheet();
    }
    catch (std::exception&) {
        std::cout << "File not found or invalid format. Creating a new file.\n";
        ws = wb.active_sheet();
        ws.cell(1, 1).value("Название актива");
        ws.cell(1, 2).value("Количество");
        ws.cell(1, 3).value("Цена покупки");
        ws.cell(1, 4).value("Текущая цена");
        ws.cell(1, 5).value("Сумма инвестиций");
        ws.cell(1, 6).value("Текущая стоимость");
        ws.cell(1, 7).value("Прибыль/Убыток");
        ws.cell(1, 8).value("Доходность");
    }

    int choice;
    do {
        std::cout << "1. Add data\n";
        std::cout << "2. Delete data\n";
        std::cout << "3. Update data\n";
        std::cout << "4. Calculate parameters\n";
        std::cout << "5. Save and exit\n";
        std::cout << "Enter your choice: ";
        std::cin >> choice;

        if (choice == 1  choice == 2  choice == 3) {
            int row, col;
            std::string data;
            std::cout << "Enter row and column: ";
            std::cin >> row >> col;

            if (choice == 1) {
                std::cout << "Enter data to add: ";
                std::cin >> data;
                addData(ws, row, col, data);
            }
            else if (choice == 2) {
                deleteData(ws, row, col);
            }
            else if (choice == 3) {
                std::cout << "Enter new data: ";
                std::cin >> data;
                updateData(ws, row, col, data);
            }
        }
        else if (choice == 4) {
            calculateParameters(ws);
            std::cout << "Parameters calculated.\n";
        }

    } while (choice != 5);

    wb.save(filename);

    std::cout << "Excel file saved successfully.\n";

    return 0;
}