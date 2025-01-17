import React, { useState, useEffect } from "react";
import API from "../services/api";

const Profile = () => {
    const [wallets, setWallets] = useState<string[]>([]); // Liste des wallets
    const [newWallet, setNewWallet] = useState<string>(""); // Wallet affiché dans l'input

    useEffect(() => {
        const fetchWallets = async () => {
            try {
                const { data } = await API.get("profile/wallets/evolution");
                setWallets(data.wallets || []); // Charger la liste des wallets
                if (data.wallets.length > 0) {
                    setNewWallet(data.wallets[0]); // Afficher le premier wallet dans l'input
                }
            } catch (error) {
                console.error("Failed to fetch wallet");
            }
        };

        fetchWallets();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        console.log(newWallet);

        // Ajouter le nouveau wallet à la liste
        const updatedWallets = [...wallets, newWallet];

        try {
            await API.put("/profile/wallets/evolution", {
                wallets: updatedWallets.map((address) => ({ address }))
            });
            setWallets(updatedWallets); // Mettre à jour l'état
            alert("Wallet updated successfully");
        } catch (error) {
            console.error("Failed to update wallet");
        }
    };

    return (
        <div className="max-w-md mx-auto p-4 space-y-4">
            <h1 className="text-2xl font-bold">Profile</h1>
            <form onSubmit={handleSubmit} className="space-y-4">
                <input
                    type="text"
                    placeholder="Add Wallet"
                    value={newWallet}
                    onChange={(e) => setNewWallet(e.target.value)}
                    className="w-full p-2 border rounded"
                />
                <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">
                    Update Wallet
                </button>
            </form>
            <h2 className="text-xl font-bold mt-4">Existing Wallets</h2>
            <ul className="list-disc pl-5">
                {wallets.map((wallet, index) => (
                    <li key={index}>{wallet}</li>
                ))}
            </ul>
        </div>
    );
};

export default Profile;
